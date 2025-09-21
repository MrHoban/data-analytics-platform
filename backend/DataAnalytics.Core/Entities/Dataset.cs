using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DataAnalytics.Core.Entities;

[Table("data_sources", Schema = "analytics")]
public class DataSource
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [MaxLength(255)]
    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Column("description")]
    public string? Description { get; set; }

    [Required]
    [MaxLength(50)]
    [Column("source_type")]
    public string SourceType { get; set; } = string.Empty; // 'file', 'api', 'database', 'stream'

    [Column("connection_config", TypeName = "jsonb")]
    public string ConnectionConfig { get; set; } = "{}";

    [Column("schema_definition", TypeName = "jsonb")]
    public string SchemaDefinition { get; set; } = "{}";

    [Column("is_active")]
    public bool IsActive { get; set; } = true;

    [Column("created_by")]
    public Guid? CreatedBy { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    [ForeignKey("CreatedBy")]
    public virtual User? Creator { get; set; }

    public virtual ICollection<Dataset> Datasets { get; set; } = new List<Dataset>();
}

[Table("datasets", Schema = "analytics")]
public class Dataset
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [MaxLength(255)]
    [Column("name")]
    public string Name { get; set; } = string.Empty;

    [Column("description")]
    public string? Description { get; set; }

    [Column("data_source_id")]
    public Guid? DataSourceId { get; set; }

    [MaxLength(500)]
    [Column("file_path")]
    public string? FilePath { get; set; }

    [Column("file_size")]
    public long? FileSize { get; set; }

    [MaxLength(50)]
    [Column("file_type")]
    public string? FileType { get; set; }

    [Column("row_count")]
    public int? RowCount { get; set; }

    [Column("column_count")]
    public int? ColumnCount { get; set; }

    [Column("schema_info", TypeName = "jsonb")]
    public string SchemaInfo { get; set; } = "{}";

    [Column("metadata", TypeName = "jsonb")]
    public string Metadata { get; set; } = "{}";

    [MaxLength(50)]
    [Column("status")]
    public string Status { get; set; } = "uploaded"; // 'uploaded', 'processing', 'processed', 'error'

    [Column("error_message")]
    public string? ErrorMessage { get; set; }

    [Column("created_by")]
    public Guid? CreatedBy { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    [ForeignKey("DataSourceId")]
    public virtual DataSource? DataSource { get; set; }

    [ForeignKey("CreatedBy")]
    public virtual User? Creator { get; set; }

    public virtual ICollection<ProcessingJob> ProcessingJobs { get; set; } = new List<ProcessingJob>();
    public virtual ICollection<MlModel> MlModels { get; set; } = new List<MlModel>();
    public virtual ICollection<Report> Reports { get; set; } = new List<Report>();

    // Computed properties
    [NotMapped]
    public bool IsProcessed => Status == "processed";

    [NotMapped]
    public bool HasError => Status == "error";

    [NotMapped]
    public string FileSizeFormatted => FileSize.HasValue ? FormatFileSize(FileSize.Value) : "Unknown";

    private static string FormatFileSize(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double len = bytes;
        int order = 0;
        while (len >= 1024 && order < sizes.Length - 1)
        {
            order++;
            len = len / 1024;
        }
        return $"{len:0.##} {sizes[order]}";
    }
}

[Table("processing_jobs", Schema = "analytics")]
public class ProcessingJob
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("dataset_id")]
    public Guid? DatasetId { get; set; }

    [Required]
    [MaxLength(50)]
    [Column("job_type")]
    public string JobType { get; set; } = string.Empty; // 'cleaning', 'transformation', 'analysis', 'ml_training'

    [Column("configuration", TypeName = "jsonb")]
    public string Configuration { get; set; } = "{}";

    [MaxLength(50)]
    [Column("status")]
    public string Status { get; set; } = "pending"; // 'pending', 'running', 'completed', 'failed'

    [Column("progress_percentage")]
    public int ProgressPercentage { get; set; } = 0;

    [Column("started_at")]
    public DateTime? StartedAt { get; set; }

    [Column("completed_at")]
    public DateTime? CompletedAt { get; set; }

    [Column("error_message")]
    public string? ErrorMessage { get; set; }

    [Column("result_data", TypeName = "jsonb")]
    public string ResultData { get; set; } = "{}";

    [Column("created_by")]
    public Guid? CreatedBy { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    [ForeignKey("DatasetId")]
    public virtual Dataset? Dataset { get; set; }

    [ForeignKey("CreatedBy")]
    public virtual User? Creator { get; set; }

    // Computed properties
    [NotMapped]
    public bool IsCompleted => Status == "completed";

    [NotMapped]
    public bool IsRunning => Status == "running";

    [NotMapped]
    public bool HasFailed => Status == "failed";

    [NotMapped]
    public TimeSpan? Duration => CompletedAt.HasValue && StartedAt.HasValue 
        ? CompletedAt.Value - StartedAt.Value 
        : null;
}
