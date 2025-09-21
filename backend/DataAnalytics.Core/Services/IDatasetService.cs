namespace DataAnalytics.Core.Services;

public interface IDatasetService
{
    Task<object> GetUserDatasetsAsync(string userId, int page = 1, int pageSize = 20);
    Task<object?> GetDatasetByIdAsync(string id);
    Task<object> CreateDatasetAsync(object dataset);
    Task<object> UpdateDatasetAsync(object dataset);
    Task<bool> DeleteDatasetAsync(string id);
    Task<object> GetDatasetStatisticsAsync(string id);
    Task<object> SearchDatasetsAsync(string query, string userId, int page = 1, int pageSize = 20);
}


