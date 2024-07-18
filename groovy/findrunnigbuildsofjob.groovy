import jenkins.model.Jenkins
import hudson.model.Run

// Replace with the full name of the job you are interested in
def jobName = "your-job-name"

def job = Jenkins.instance.getItemByFullName(jobName)

if (job == null) {
    println "Job not found: ${jobName}"
} else {
    def runningBuilds = job.builds.findAll { it.isBuilding() }
    
    if (runningBuilds.isEmpty()) {
        println "No running builds for job: ${jobName}"
    } else {
        println "Running builds for job: ${jobName}"
        runningBuilds.each { build ->
            println "Build #${build.number}, started at ${build.getTimestampString()}"
        }
    }
}