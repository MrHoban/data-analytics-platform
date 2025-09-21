using Microsoft.EntityFrameworkCore;
using DataAnalytics.Core.Entities;
using System.Text.Json;

namespace DataAnalytics.Data;

public class DataAnalyticsDbContext : DbContext
{
    public DataAnalyticsDbContext(DbContextOptions<DataAnalyticsDbContext> options) : base(options)
    {
    }

    // Auth Schema
    public DbSet<User> Users { get; set; }
    public DbSet<Role> Roles { get; set; }
    public DbSet<UserRole> UserRoles { get; set; }
    public DbSet<UserSession> UserSessions { get; set; }

    // Analytics Schema
    public DbSet<DataSource> DataSources { get; set; }
    public DbSet<Dataset> Datasets { get; set; }
    public DbSet<ProcessingJob> ProcessingJobs { get; set; }
    public DbSet<MlModel> MlModels { get; set; }
    public DbSet<ModelPrediction> ModelPredictions { get; set; }
    public DbSet<Report> Reports { get; set; }

    // Audit Schema
    public DbSet<ActivityLog> ActivityLogs { get; set; }
    public DbSet<SystemLog> SystemLogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure schemas
        modelBuilder.HasDefaultSchema("public");

        // Configure composite keys
        modelBuilder.Entity<UserRole>()
            .HasKey(ur => new { ur.UserId, ur.RoleId });

        // Configure relationships
        ConfigureUserRelationships(modelBuilder);
        ConfigureAnalyticsRelationships(modelBuilder);
        ConfigureAuditRelationships(modelBuilder);

        // Configure JSON columns
        ConfigureJsonColumns(modelBuilder);

        // Configure indexes
        ConfigureIndexes(modelBuilder);

        // Configure constraints
        ConfigureConstraints(modelBuilder);
    }

    private static void ConfigureUserRelationships(ModelBuilder modelBuilder)
    {
        // User -> UserRoles
        modelBuilder.Entity<User>()
            .HasMany(u => u.UserRoles)
            .WithOne(ur => ur.User)
            .HasForeignKey(ur => ur.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        // Role -> UserRoles
        modelBuilder.Entity<Role>()
            .HasMany(r => r.UserRoles)
            .WithOne(ur => ur.Role)
            .HasForeignKey(ur => ur.RoleId)
            .OnDelete(DeleteBehavior.Cascade);

        // User -> UserSessions
        modelBuilder.Entity<User>()
            .HasMany(u => u.UserSessions)
            .WithOne(us => us.User)
            .HasForeignKey(us => us.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        // UserRole -> AssignedByUser
        modelBuilder.Entity<UserRole>()
            .HasOne(ur => ur.AssignedByUser)
            .WithMany()
            .HasForeignKey(ur => ur.AssignedBy)
            .OnDelete(DeleteBehavior.SetNull);
    }

    private static void ConfigureAnalyticsRelationships(ModelBuilder modelBuilder)
    {
        // DataSource -> Datasets
        modelBuilder.Entity<DataSource>()
            .HasMany(ds => ds.Datasets)
            .WithOne(d => d.DataSource)
            .HasForeignKey(d => d.DataSourceId)
            .OnDelete(DeleteBehavior.SetNull);

        // Dataset -> ProcessingJobs
        modelBuilder.Entity<Dataset>()
            .HasMany(d => d.ProcessingJobs)
            .WithOne(pj => pj.Dataset)
            .HasForeignKey(pj => pj.DatasetId)
            .OnDelete(DeleteBehavior.SetNull);

        // Dataset -> MlModels
        modelBuilder.Entity<Dataset>()
            .HasMany(d => d.MlModels)
            .WithOne(m => m.Dataset)
            .HasForeignKey(m => m.DatasetId)
            .OnDelete(DeleteBehavior.SetNull);

        // Dataset -> Reports
        modelBuilder.Entity<Dataset>()
            .HasMany(d => d.Reports)
            .WithOne(r => r.Dataset)
            .HasForeignKey(r => r.DatasetId)
            .OnDelete(DeleteBehavior.SetNull);

        // MlModel -> ModelPredictions
        modelBuilder.Entity<MlModel>()
            .HasMany(m => m.Predictions)
            .WithOne(p => p.Model)
            .HasForeignKey(p => p.ModelId)
            .OnDelete(DeleteBehavior.Cascade);

        // User relationships for analytics entities
        modelBuilder.Entity<DataSource>()
            .HasOne(ds => ds.Creator)
            .WithMany()
            .HasForeignKey(ds => ds.CreatedBy)
            .OnDelete(DeleteBehavior.SetNull);

        modelBuilder.Entity<Dataset>()
            .HasOne(d => d.Creator)
            .WithMany(u => u.Datasets)
            .HasForeignKey(d => d.CreatedBy)
            .OnDelete(DeleteBehavior.SetNull);

        modelBuilder.Entity<ProcessingJob>()
            .HasOne(pj => pj.Creator)
            .WithMany()
            .HasForeignKey(pj => pj.CreatedBy)
            .OnDelete(DeleteBehavior.SetNull);

        modelBuilder.Entity<MlModel>()
            .HasOne(m => m.Creator)
            .WithMany(u => u.MlModels)
            .HasForeignKey(m => m.CreatedBy)
            .OnDelete(DeleteBehavior.SetNull);

        modelBuilder.Entity<ModelPrediction>()
            .HasOne(p => p.Creator)
            .WithMany()
            .HasForeignKey(p => p.CreatedBy)
            .OnDelete(DeleteBehavior.SetNull);

        modelBuilder.Entity<Report>()
            .HasOne(r => r.Creator)
            .WithMany(u => u.Reports)
            .HasForeignKey(r => r.CreatedBy)
            .OnDelete(DeleteBehavior.SetNull);
    }

    private static void ConfigureAuditRelationships(ModelBuilder modelBuilder)
    {
        // ActivityLog -> User
        modelBuilder.Entity<ActivityLog>()
            .HasOne(al => al.User)
            .WithMany()
            .HasForeignKey(al => al.UserId)
            .OnDelete(DeleteBehavior.SetNull);
    }

    private static void ConfigureJsonColumns(ModelBuilder modelBuilder)
    {
        // Configure JSONB columns for PostgreSQL
        modelBuilder.Entity<Role>()
            .Property(r => r.Permissions)
            .HasColumnType("jsonb");

        modelBuilder.Entity<DataSource>()
            .Property(ds => ds.ConnectionConfig)
            .HasColumnType("jsonb");

        modelBuilder.Entity<DataSource>()
            .Property(ds => ds.SchemaDefinition)
            .HasColumnType("jsonb");

        modelBuilder.Entity<Dataset>()
            .Property(d => d.SchemaInfo)
            .HasColumnType("jsonb");

        modelBuilder.Entity<Dataset>()
            .Property(d => d.Metadata)
            .HasColumnType("jsonb");

        modelBuilder.Entity<ProcessingJob>()
            .Property(pj => pj.Configuration)
            .HasColumnType("jsonb");

        modelBuilder.Entity<ProcessingJob>()
            .Property(pj => pj.ResultData)
            .HasColumnType("jsonb");

        modelBuilder.Entity<MlModel>()
            .Property(m => m.TrainingConfig)
            .HasColumnType("jsonb");

        modelBuilder.Entity<MlModel>()
            .Property(m => m.ModelMetrics)
            .HasColumnType("jsonb");

        modelBuilder.Entity<ModelPrediction>()
            .Property(p => p.InputData)
            .HasColumnType("jsonb");

        modelBuilder.Entity<ModelPrediction>()
            .Property(p => p.PredictionResult)
            .HasColumnType("jsonb");

        modelBuilder.Entity<Report>()
            .Property(r => r.Configuration)
            .HasColumnType("jsonb");

        modelBuilder.Entity<Report>()
            .Property(r => r.ChartData)
            .HasColumnType("jsonb");

        modelBuilder.Entity<ActivityLog>()
            .Property(al => al.Details)
            .HasColumnType("jsonb");

        modelBuilder.Entity<SystemLog>()
            .Property(sl => sl.Details)
            .HasColumnType("jsonb");
    }

    private static void ConfigureIndexes(ModelBuilder modelBuilder)
    {
        // User indexes
        modelBuilder.Entity<User>()
            .HasIndex(u => u.Email)
            .IsUnique();

        modelBuilder.Entity<User>()
            .HasIndex(u => u.IsActive);

        // UserSession indexes
        modelBuilder.Entity<UserSession>()
            .HasIndex(us => us.SessionToken)
            .IsUnique();

        modelBuilder.Entity<UserSession>()
            .HasIndex(us => us.UserId);

        // Dataset indexes
        modelBuilder.Entity<Dataset>()
            .HasIndex(d => d.Status);

        modelBuilder.Entity<Dataset>()
            .HasIndex(d => d.CreatedBy);

        modelBuilder.Entity<Dataset>()
            .HasIndex(d => d.CreatedAt);

        // ProcessingJob indexes
        modelBuilder.Entity<ProcessingJob>()
            .HasIndex(pj => pj.Status);

        modelBuilder.Entity<ProcessingJob>()
            .HasIndex(pj => pj.DatasetId);

        // MlModel indexes
        modelBuilder.Entity<MlModel>()
            .HasIndex(m => m.Status);

        modelBuilder.Entity<MlModel>()
            .HasIndex(m => m.IsActive);

        // ActivityLog indexes
        modelBuilder.Entity<ActivityLog>()
            .HasIndex(al => al.UserId);

        modelBuilder.Entity<ActivityLog>()
            .HasIndex(al => al.Timestamp);

        modelBuilder.Entity<ActivityLog>()
            .HasIndex(al => al.Action);

        // SystemLog indexes
        modelBuilder.Entity<SystemLog>()
            .HasIndex(sl => sl.Level);

        modelBuilder.Entity<SystemLog>()
            .HasIndex(sl => sl.Timestamp);
    }

    private static void ConfigureConstraints(ModelBuilder modelBuilder)
    {
        // Email format validation is handled by data annotations
        // Additional constraints can be added here if needed
    }

    public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        // Update timestamps
        var entries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Added || e.State == EntityState.Modified);

        foreach (var entry in entries)
        {
            if (entry.Entity is User user)
            {
                if (entry.State == EntityState.Added)
                    user.CreatedAt = DateTime.UtcNow;
                user.UpdatedAt = DateTime.UtcNow;
            }
            else if (entry.Entity is DataSource dataSource)
            {
                if (entry.State == EntityState.Added)
                    dataSource.CreatedAt = DateTime.UtcNow;
                dataSource.UpdatedAt = DateTime.UtcNow;
            }
            else if (entry.Entity is Dataset dataset)
            {
                if (entry.State == EntityState.Added)
                    dataset.CreatedAt = DateTime.UtcNow;
                dataset.UpdatedAt = DateTime.UtcNow;
            }
            else if (entry.Entity is MlModel mlModel)
            {
                if (entry.State == EntityState.Added)
                    mlModel.CreatedAt = DateTime.UtcNow;
                mlModel.UpdatedAt = DateTime.UtcNow;
            }
            else if (entry.Entity is Report report)
            {
                if (entry.State == EntityState.Added)
                    report.CreatedAt = DateTime.UtcNow;
                report.UpdatedAt = DateTime.UtcNow;
            }
        }

        return await base.SaveChangesAsync(cancellationToken);
    }
}
