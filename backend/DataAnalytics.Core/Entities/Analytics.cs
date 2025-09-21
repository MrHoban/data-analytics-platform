using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DataAnalytics.Core.Entities;

[Table("ml_models", Schema = "analytics")]
public class MlModel
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
    [MaxLength(100)]
    [Column("model_type")]
    public string ModelType { get; set; } = string.Empty; // 'regression', 'classification', 'clustering', etc.

    [Required]
    [MaxLength(100)]
    [Column("algorithm")]
    public string Algorithm { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    [Column("version")]
    public string Version { get; set; } = string.Empty;

    [Column("dataset_id")]
    public Guid? DatasetId { get; set; }

    [Column("training_config", TypeName = "jsonb")]
    public string TrainingConfig { get; set; } = "{}";

    [Column("model_metrics", TypeName = "jsonb")]
    public string ModelMetrics { get; set; } = "{}";

    [MaxLength(500)]
    [Column("model_path")]
    public string? ModelPath { get; set; }

    [MaxLength(50)]
    [Column("status")]
    public string Status { get; set; } = "training"; // 'training', 'trained', 'deployed', 'archived'

    [Column("is_active")]
    public bool IsActive { get; set; } = true;

    [Column("created_by")]
    public Guid? CreatedBy { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    [ForeignKey("DatasetId")]
    public virtual Dataset? Dataset { get; set; }

    [ForeignKey("CreatedBy")]
    public virtual User? Creator { get; set; }

    public virtual ICollection<ModelPrediction> Predictions { get; set; } = new List<ModelPrediction>();

    // Computed properties
    [NotMapped]
    public bool IsTrained => Status == "trained" || Status == "deployed";

    [NotMapped]
    public bool IsDeployed => Status == "deployed";

    [NotMapped]
    public bool IsTraining => Status == "training";
}

[Table("model_predictions", Schema = "analytics")]
public class ModelPrediction
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("model_id")]
    public Guid ModelId { get; set; }

    [Required]
    [Column("input_data", TypeName = "jsonb")]
    public string InputData { get; set; } = string.Empty;

    [Required]
    [Column("prediction_result", TypeName = "jsonb")]
    public string PredictionResult { get; set; } = string.Empty;

    [Column("confidence_score")]
    public decimal? ConfidenceScore { get; set; }

    [Column("prediction_time")]
    public DateTime PredictionTime { get; set; } = DateTime.UtcNow;

    [Column("created_by")]
    public Guid? CreatedBy { get; set; }

    // Navigation properties
    [ForeignKey("ModelId")]
    public virtual MlModel Model { get; set; } = null!;

    [ForeignKey("CreatedBy")]
    public virtual User? Creator { get; set; }
}

[Table("reports", Schema = "analytics")]
public class Report
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
    [Column("report_type")]
    public string ReportType { get; set; } = string.Empty; // 'dashboard', 'chart', 'table', 'export'

    [Column("dataset_id")]
    public Guid? DatasetId { get; set; }

    [Column("configuration", TypeName = "jsonb")]
    public string Configuration { get; set; } = "{}";

    [Column("chart_data", TypeName = "jsonb")]
    public string ChartData { get; set; } = "{}";

    [Column("is_public")]
    public bool IsPublic { get; set; } = false;

    [Column("created_by")]
    public Guid? CreatedBy { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    // Navigation properties
    [ForeignKey("DatasetId")]
    public virtual Dataset? Dataset { get; set; }

    [ForeignKey("CreatedBy")]
    public virtual User? Creator { get; set; }
}

[Table("activity_log", Schema = "audit")]
public class ActivityLog
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("user_id")]
    public Guid? UserId { get; set; }

    [Required]
    [MaxLength(100)]
    [Column("action")]
    public string Action { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    [Column("resource_type")]
    public string ResourceType { get; set; } = string.Empty;

    [Column("resource_id")]
    public Guid? ResourceId { get; set; }

    [Column("details", TypeName = "jsonb")]
    public string Details { get; set; } = "{}";

    [Column("ip_address")]
    public string? IpAddress { get; set; }

    [Column("user_agent")]
    public string? UserAgent { get; set; }

    [Column("timestamp")]
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    // Navigation properties
    [ForeignKey("UserId")]
    public virtual User? User { get; set; }
}

[Table("system_logs", Schema = "audit")]
public class SystemLog
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [MaxLength(20)]
    [Column("level")]
    public string Level { get; set; } = string.Empty; // 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'

    [Required]
    [Column("message")]
    public string Message { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    [Column("source")]
    public string Source { get; set; } = string.Empty; // 'api', 'python-engine', 'frontend'

    [Column("details", TypeName = "jsonb")]
    public string Details { get; set; } = "{}";

    [Column("timestamp")]
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}
