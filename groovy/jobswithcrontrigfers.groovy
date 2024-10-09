// Groovy script to list jobs with cron triggers
import jenkins.model.*
import hudson.triggers.TimerTrigger

def jenkins = Jenkins.instance

jenkins.getAllItems(Job.class).each { job ->
    def cronTrigger = job.getTriggers().get(TimerTrigger.class)
    if (cronTrigger != null) {
        println("Job: ${job.fullName} has a cron trigger: ${cronTrigger.spec}")
    }
}