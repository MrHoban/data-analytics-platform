using System.ComponentModel.DataAnnotations;

namespace DataAnalytics.Core.Models;

public class Dataset
{
    [Key]
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    [Required]
    [MaxLength(255)]
    public string Name { get; set; } = string.Empty;
    
    [MaxLength(1000)]
    public string Description { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(255)]
    public string FileName { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(255)]
    public string FilePath { get; set; } = string.Empty;
    
    public long FileSize { get; set; }
    
    [Required]
    [MaxLength(50)]
    public string Status { get; set; } = "uploaded";
    
    [Required]
    public string UserId { get; set; } = string.Empty;
    
    public string? Metadata { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // Navigation properties
    public virtual ICollection<MLModel> MLModels { get; set; } = new List<MLModel>();
    public virtual ICollection<Report> Reports { get; set; } = new List<Report>();
}

public class MLModel
{
    [Key]
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    [Required]
    [MaxLength(255)]
    public string Name { get; set; } = string.Empty;
    
    [MaxLength(1000)]
    public string Description { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(100)]
    public string Algorithm { get; set; } = string.Empty;
    
    [Required]
    public string DatasetId { get; set; } = string.Empty;
    
    [Required]
    public string UserId { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(50)]
    public string Status { get; set; } = "training";
    
    public string? Hyperparameters { get; set; }
    
    public string? Metrics { get; set; }
    
    [MaxLength(255)]
    public string? ModelPath { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // Navigation properties
    public virtual Dataset Dataset { get; set; } = null!;
}

public class Report
{
    [Key]
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    [Required]
    [MaxLength(255)]
    public string Title { get; set; } = string.Empty;
    
    [MaxLength(1000)]
    public string Description { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(100)]
    public string ReportType { get; set; } = string.Empty;
    
    [Required]
    public string DatasetId { get; set; } = string.Empty;
    
    [Required]
    public string UserId { get; set; } = string.Empty;
    
    public string? Configuration { get; set; }
    
    public string? Content { get; set; }
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // Navigation properties
    public virtual Dataset Dataset { get; set; } = null!;
}
