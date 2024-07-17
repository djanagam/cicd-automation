import jenkins.model.Jenkins
import hudson.model.Job

def getCredentialIdsFromJob(job) {
    def credentialIds = []
    def jobConfigXml = job.getConfigFile().asString()

    def pattern = /<credentialsId>(.*?)<\/credentialsId>/
    def matcher = (jobConfigXml =~ pattern)

    while (matcher.find()) {
        credentialIds.add(matcher.group(1))
    }

    return credentialIds
}

def allJobs = Jenkins.instance.getAllItems(Job.class)
def jobCredentialsMap = [:]

allJobs.each { job ->
    def credentialIds = getCredentialIdsFromJob(job)
    if (!credentialIds.isEmpty()) {
        def lastBuild = job.getLastBuild()
        def lastBuildTime = lastBuild?.getTime() ?: 'Never Built'
        jobCredentialsMap[job.fullName] = [credentials: credentialIds, lastBuildTime: lastBuildTime]
    }
}

println "Job -> Credentials mapping with last build activity:"
jobCredentialsMap.each { jobName, data ->
    println "${jobName}: Credentials [${data.credentials.join(', ')}], Last Build Time [${data.lastBuildTime}]"
}