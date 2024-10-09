// Groovy script to list jobs with cron triggers, their enabled/disabled status, and cron schedule
import jenkins.model.*
import hudson.triggers.TimerTrigger

def jenkins = Jenkins.instance

jenkins.getAllItems(Job.class).each { job ->
    def cronTrigger = job.getTriggers().get(TimerTrigger.class)
    if (cronTrigger != null) {
        def status = job.isDisabled() ? "DISABLED" : "ENABLED"
        def cronSchedule = cronTrigger.spec
        println("Job: ${job.fullName} is ${status}, Cron Schedule: ${cronSchedule}")
    }
}