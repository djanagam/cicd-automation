import jenkins.model.Jenkins
import hudson.model.Job

def getCredentialIdsFromJob(job) {
    def credentialIds = []
    try {
        def jobConfigXml = job.getConfigFile().asString()
        def pattern = /<credentialsId>(.*?)<\/credentialsId>/
        def matcher = (jobConfigXml =~ pattern)

        while (matcher.find()) {
            credentialIds.add(matcher.group(1))
        }
    } catch (Exception e) {
        println "Error processing job ${job.fullName}: ${e.message}"
    }
    return credentialIds
}

def allJobs = Jenkins.instance.getAllItems(Job.class)
def jobCredentialsMap = []

allJobs.each { job ->
    def credentialIds = getCredentialIdsFromJob(job)
    if (!credentialIds.isEmpty()) {
        def lastBuild = job.getLastBuild()
        def lastBuildTime = lastBuild?.getTime() ?: 'Never Built'
        jobCredentialsMap << [job.fullName, credentialIds.join(';'), lastBuildTime]
    }
}

// Print CSV header
println "Job,Credentials,Last Built"

jobCredentialsMap.each { data ->
    println "\"${data[0]}\",\"${data[1]}\",\"${data[2]}\""
}