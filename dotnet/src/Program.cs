using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using Octokit;
using System.Text.Json;

namespace TpmAgent;

public class Program
{
    public static async Task Main(string[] args)
    {
        // Setup configuration
        var configuration = new ConfigurationBuilder()
            .AddEnvironmentVariables()
            .Build();

        // Setup dependency injection
        var services = new ServiceCollection();
        services.AddLogging(builder =>
        {
            builder.AddConsole();
            builder.SetMinimumLevel(LogLevel.Information);
        });

        var serviceProvider = services.BuildServiceProvider();
        var logger = serviceProvider.GetRequiredService<ILogger<Program>>();

        logger.LogInformation("Starting TPM Agent with Semantic Kernel Process Framework...");

        try
        {
            // Parse GitHub Action inputs
            var issueContent = Environment.GetEnvironmentVariable("INPUT_ISSUE_CONTENT") ?? "";
            var githubToken = Environment.GetEnvironmentVariable("INPUT_GITHUB_TOKEN") ?? "";
            var repository = Environment.GetEnvironmentVariable("INPUT_REPOSITORY") ?? "";
            var issueNumber = Environment.GetEnvironmentVariable("INPUT_ISSUE_NUMBER") ?? "";

            logger.LogInformation($"Processing issue #{issueNumber} from {repository}");

            if (string.IsNullOrEmpty(issueContent))
            {
                throw new ArgumentException("Issue content is required");
            }

            if (string.IsNullOrEmpty(githubToken))
            {
                throw new ArgumentException("GitHub token is required");
            }

            if (string.IsNullOrEmpty(repository))
            {
                throw new ArgumentException("Repository is required");
            }

            if (string.IsNullOrEmpty(issueNumber) || !int.TryParse(issueNumber, out int issueNum))
            {
                throw new ArgumentException("Valid issue number is required");
            }

            // Create GitHub client
            var github = new GitHubClient(new ProductHeaderValue("tpm-agent"))
            {
                Credentials = new Credentials(githubToken)
            };

            // Create and run the issue processing agent using Process Framework pattern
            var agent = new IssueProcessingAgent(logger, github);
            var result = await agent.ProcessIssueAsync(issueContent, repository, issueNum);
            
            logger.LogInformation($"Issue processing completed: {result}");
            
            // Set GitHub Actions outputs
            await SetGitHubOutput("result", result);
            await SetGitHubOutput("status", "success");
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error occurred during issue processing");
            
            await SetGitHubOutput("result", $"Error: {ex.Message}");
            await SetGitHubOutput("status", "error");
            
            Environment.Exit(1);
        }
    }

    private static async Task SetGitHubOutput(string name, string value)
    {
        var outputFile = Environment.GetEnvironmentVariable("GITHUB_OUTPUT");
        var outputLine = $"{name}={value}";
        
        if (!string.IsNullOrEmpty(outputFile))
        {
            await File.AppendAllTextAsync(outputFile, outputLine + Environment.NewLine);
        }
        else
        {
            // Fallback for testing
            await File.AppendAllTextAsync("/tmp/github_output.txt", outputLine + Environment.NewLine);
        }
    }
}

public class IssueProcessingAgent
{
    private readonly ILogger _logger;
    private readonly GitHubClient _github;
    private readonly Kernel _kernel;

    public IssueProcessingAgent(ILogger logger, GitHubClient github)
    {
        _logger = logger;
        _github = github;
        
        // Create kernel for process-like workflow
        var builder = Kernel.CreateBuilder();
        _kernel = builder.Build();
    }

    public async Task<string> ProcessIssueAsync(string issueContent, string repository, int issueNumber)
    {
        _logger.LogInformation($"Starting issue processing with Semantic Kernel Process Framework pattern");

        try
        {
            // Execute process steps in sequence (simulating Process Framework)
            var processContext = new ProcessContext
            {
                IssueContent = issueContent,
                Repository = repository,
                IssueNumber = issueNumber,
                GitHub = _github,
                Logger = _logger
            };

            // Step 1: Analyze the issue
            var analysisResult = await ExecuteAnalysisStepAsync(processContext);
            processContext.Analysis = analysisResult;

            // Step 2: Generate comment
            var comment = await ExecuteCommentGenerationStepAsync(processContext);
            processContext.GeneratedComment = comment;

            // Step 3: Post comment to GitHub
            await ExecutePostCommentStepAsync(processContext);

            return "Issue processed successfully using Semantic Kernel Process Framework pattern";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in issue processing");
            throw;
        }
    }

    private async Task<IssueAnalysis> ExecuteAnalysisStepAsync(ProcessContext context)
    {
        context.Logger.LogInformation("::group::Analyzing issue content");
        
        try
        {
            // Analyze the issue content using simple logic
            // In a real implementation, this would use Semantic Kernel's AI capabilities
            var analysis = new IssueAnalysis();
            
            var content = context.IssueContent.ToLower();
            
            // Determine issue type
            if (content.Contains("bug") || content.Contains("error") || content.Contains("issue"))
            {
                analysis.Type = "bug";
            }
            else if (content.Contains("feature") || content.Contains("enhancement") || content.Contains("request"))
            {
                analysis.Type = "feature";
            }
            else
            {
                analysis.Type = "question";
            }

            // Determine priority
            if (content.Contains("urgent") || content.Contains("critical") || content.Contains("high"))
            {
                analysis.Priority = "high";
            }
            else if (content.Contains("low") || content.Contains("minor"))
            {
                analysis.Priority = "low";
            }
            else
            {
                analysis.Priority = "medium";
            }

            // Extract key topics
            var topics = new List<string>();
            if (content.Contains("tpm")) topics.Add("TPM");
            if (content.Contains("security")) topics.Add("Security");
            if (content.Contains("authentication")) topics.Add("Authentication");
            if (content.Contains("encryption")) topics.Add("Encryption");
            if (content.Contains("docker")) topics.Add("Docker");
            if (content.Contains("container")) topics.Add("Container");
            
            analysis.Topics = topics;
            analysis.Summary = context.IssueContent.Length > 100 
                ? context.IssueContent.Substring(0, 100) + "..."
                : context.IssueContent;

            context.Logger.LogInformation($"Analysis completed - Type: {analysis.Type}, Priority: {analysis.Priority}, Topics: {string.Join(", ", analysis.Topics)}");
            
            // Simulate some async work
            await Task.Delay(10);
            
            return analysis;
        }
        finally
        {
            context.Logger.LogInformation("::endgroup::");
        }
    }

    private async Task<string> ExecuteCommentGenerationStepAsync(ProcessContext context)
    {
        context.Logger.LogInformation("::group::Generating response comment");
        
        try
        {
            // Generate a response comment based on the analysis
            var comment = await Task.FromResult(GenerateContextualComment(context.Analysis, context.IssueContent));
            
            context.Logger.LogInformation($"Generated comment with {comment.Length} characters");
            
            return comment;
        }
        finally
        {
            context.Logger.LogInformation("::endgroup::");
        }
    }

    private async Task ExecutePostCommentStepAsync(ProcessContext context)
    {
        context.Logger.LogInformation("::group::Posting comment to GitHub");
        
        try
        {
            var repoParts = context.Repository.Split('/');
            if (repoParts.Length != 2)
            {
                throw new ArgumentException("Repository must be in format owner/repo");
            }
            
            var owner = repoParts[0];
            var repo = repoParts[1];
            
            // Post the comment to GitHub
            await context.GitHub.Issue.Comment.Create(owner, repo, context.IssueNumber, context.GeneratedComment);
            
            context.Logger.LogInformation($"Comment posted successfully to {context.Repository}#{context.IssueNumber}");
        }
        finally
        {
            context.Logger.LogInformation("::endgroup::");
        }
    }

    private string GenerateContextualComment(IssueAnalysis analysis, string issueContent)
    {
        var comment = "Thank you for this issue! I've analyzed it using the Semantic Kernel Process Framework.\n\n";
        
        comment += "## Analysis Results\n\n";
        comment += $"- **Type**: {analysis.Type}\n";
        comment += $"- **Priority**: {analysis.Priority}\n";
        
        if (analysis.Topics.Any())
        {
            comment += $"- **Topics**: {string.Join(", ", analysis.Topics)}\n";
        }
        
        comment += "\n## Next Steps\n\n";
        
        switch (analysis.Type)
        {
            case "bug":
                comment += "This appears to be a bug report. The development team will:\n";
                comment += "1. Review the issue details\n";
                comment += "2. Reproduce the issue if possible\n";
                comment += "3. Investigate the root cause\n";
                comment += "4. Provide a fix or workaround\n";
                break;
                
            case "feature":
                comment += "This appears to be a feature request. The team will:\n";
                comment += "1. Evaluate the request against project goals\n";
                comment += "2. Assess implementation complexity\n";
                comment += "3. Consider adding it to the roadmap\n";
                comment += "4. Provide feedback on feasibility\n";
                break;
                
            default:
                comment += "This appears to be a question or general issue. The team will:\n";
                comment += "1. Review the details provided\n";
                comment += "2. Provide clarification or guidance\n";
                comment += "3. Update documentation if needed\n";
                break;
        }
        
        comment += "\n## Additional Information\n\n";
        
        if (analysis.Topics.Contains("TPM"))
        {
            comment += "Since this relates to TPM functionality, please ensure you have:\n";
            comment += "- TPM hardware or software available\n";
            comment += "- Proper permissions for TPM operations\n";
            comment += "- Latest version of the TPM Agent\n\n";
        }
        
        if (analysis.Topics.Contains("Docker"))
        {
            comment += "For Docker-related issues, please provide:\n";
            comment += "- Docker version information\n";
            comment += "- Container logs if applicable\n";
            comment += "- Environment details\n\n";
        }
        
        comment += "---\n";
        comment += "*This response was generated automatically using the Semantic Kernel Process Framework.*";
        
        return comment;
    }
}

public class ProcessContext
{
    public string IssueContent { get; set; } = "";
    public string Repository { get; set; } = "";
    public int IssueNumber { get; set; }
    public GitHubClient GitHub { get; set; } = null!;
    public ILogger Logger { get; set; } = null!;
    public IssueAnalysis Analysis { get; set; } = new();
    public string GeneratedComment { get; set; } = "";
}

public class IssueAnalysis
{
    public string Type { get; set; } = "";
    public string Priority { get; set; } = "";
    public List<string> Topics { get; set; } = new();
    public string Summary { get; set; } = "";
}