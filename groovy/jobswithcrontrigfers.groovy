// Groovy script to list jobs with cron triggers, their enabled/disabled status, and cron schedule
import jenkins.model.*
import hudson.triggers.TimerTrigger

def jenkins = Jenkins.instance

jenkins.getAllItems(Job.class).each { job ->
    def triggers = job.getTriggers() // Fetch all triggers for the job
    triggers.each { trigger ->
        if (trigger.value instanceof TimerTrigger) { // Check if the trigger is a cron (TimerTrigger)
            def cronTrigger = trigger.value
            def status = job.isDisabled() ? "DISABLED" : "ENABLED"
            def cronSchedule = cronTrigger.spec
            println("Job: ${job.fullName} is ${status}, Cron Schedule: ${cronSchedule}")
        }
    }
}