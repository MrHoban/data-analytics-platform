using DataAnalytics.Data;
using DataAnalytics.Core.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Serilog;
using Microsoft.OpenApi.Models;
using System.Reflection;
using FluentValidation;
using AutoMapper;
using StackExchange.Redis;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.File("logs/api-.txt", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container
var services = builder.Services;
var configuration = builder.Configuration;

// Database Configuration
services.AddDbContext<DataAnalyticsDbContext>(options =>
    options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

// Redis Configuration
services.AddSingleton<IConnectionMultiplexer>(provider =>
{
    var connectionString = configuration.GetConnectionString("Redis");
    return ConnectionMultiplexer.Connect(connectionString ?? "localhost:6379");
});

// Authentication & Authorization
var jwtSettings = configuration.GetSection("JwtSettings");
var secretKey = jwtSettings["SecretKey"] ?? throw new InvalidOperationException("JWT SecretKey is required");

services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = jwtSettings["Issuer"],
        ValidAudience = jwtSettings["Audience"],
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
        ClockSkew = TimeSpan.Zero
    };
});

services.AddAuthorization();

// CORS Configuration
services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins(
            "http://localhost:3000",
            "https://localhost:3000",
            "http://localhost:5173",
            "https://localhost:5173"
        )
        .AllowAnyMethod()
        .AllowAnyHeader()
        .AllowCredentials();
    });
});

// API Controllers
services.AddControllers();

// FluentValidation
services.AddValidatorsFromAssemblyContaining<Program>();

// AutoMapper
services.AddAutoMapper(typeof(Program));

// Swagger/OpenAPI
services.AddEndpointsApiExplorer();
services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Data Analytics Platform API",
        Version = "v1",
        Description = "A comprehensive data analytics platform API",
        Contact = new OpenApiContact
        {
            Name = "Data Analytics Team",
            Email = "support@dataanalytics.com"
        }
    });

    // Include XML comments
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath))
    {
        c.IncludeXmlComments(xmlPath);
    }

    // JWT Authentication
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme. Enter 'Bearer' [space] and then your token in the text input below.",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

// SignalR for real-time communication
services.AddSignalR();

// HTTP Client for Python service communication
services.AddHttpClient("PythonAnalyticsService", client =>
{
    var baseUrl = configuration["PythonService:BaseUrl"] ?? "http://localhost:8000";
    client.BaseAddress = new Uri(baseUrl);
    client.Timeout = TimeSpan.FromMinutes(10); // Long timeout for ML operations
});

// Health Checks
services.AddHealthChecks()
    .AddRedis(configuration.GetConnectionString("Redis") ?? "localhost:6379");

// Register application services
services.AddScoped<IPythonAnalyticsService, PythonAnalyticsService>();
services.AddScoped<ICacheService, RedisCacheService>();
services.Configure<PythonServiceOptions>(
    configuration.GetSection(PythonServiceOptions.SectionName));

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Data Analytics Platform API v1");
        c.RoutePrefix = string.Empty; // Serve Swagger UI at root
    });
}

// Security headers
app.Use(async (context, next) =>
{
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
    context.Response.Headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");
    await next();
});

app.UseHttpsRedirection();

app.UseCors("AllowFrontend");

app.UseAuthentication();
app.UseAuthorization();

// Request logging
app.UseSerilogRequestLogging();

app.MapControllers();

// Health check endpoint
app.MapHealthChecks("/health");

// SignalR hubs
// TODO: Map SignalR hubs here

// Database migration and seeding
using (var scope = app.Services.CreateScope())
{
    try
    {
        var context = scope.ServiceProvider.GetRequiredService<DataAnalyticsDbContext>();
        
        if (app.Environment.IsDevelopment())
        {
            // Auto-migrate in development
            await context.Database.MigrateAsync();
        }
        
        Log.Information("Database connection verified successfully");
    }
    catch (Exception ex)
    {
        Log.Fatal(ex, "An error occurred while connecting to the database");
        throw;
    }
}

Log.Information("Data Analytics Platform API starting up...");

try
{
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
