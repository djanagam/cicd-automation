// Get the Jenkins instance
def jenkins = Jenkins.instance

// CSV header
println "Job Name,Last Build Time,Triggered By,Last Build Status"

// Iterate over all jobs
jenkins.getAllItems(Job).each { job ->
    def jobName = job.getFullName()
    def lastBuild = job.getLastBuild()

    if (lastBuild) {
        def lastBuildTime = lastBuild.getTime() // Get last build time
        def cause = lastBuild.getCauses().find { it instanceof hudson.model.Cause.UserIdCause }
        def triggeredBy = cause ? cause.getUserId() : "Unknown/Automated"
        def lastBuildStatus = lastBuild.getResult()?.toString() ?: "In Progress"

        // Print job details in CSV format
        println "\"${jobName}\",\"${lastBuildTime}\",\"${triggeredBy}\",\"${lastBuildStatus}\""
    } else {
        // Print no builds found
        println "\"${jobName}\",\"N/A\",\"N/A\",\"No Builds Found\""
    }
}