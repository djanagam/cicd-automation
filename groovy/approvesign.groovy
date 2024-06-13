import jenkins.model.Jenkins
import org.jenkinsci.plugins.scriptsecurity.scripts.ScriptApproval
import org.jenkinsci.plugins.scriptsecurity.scripts.ScriptApproval.PendingScript

// Define your pattern or user
def pattern = "your_pattern_here" // Replace with your desired pattern
def user = "djanagam" // Replace with your desired user

// Get the script approval instance
def scriptApproval = ScriptApproval.get()

// Function to approve a script
def approveScript(PendingScript pendingScript) {
    try {
        scriptApproval.approveScript(pendingScript.hash)
        println("Approved script: ${pendingScript.script}")
    } catch (Exception e) {
        println("Failed to approve script: ${pendingScript.script}")
        e.printStackTrace()
    }
}

// Iterate through pending scripts and approve those matching the pattern or user
scriptApproval.getPendingScripts().each { pendingScript ->
    def script = pendingScript.script
    def userName = pendingScript.getContext()?.getUser()?.getId() // Adjusting the method to get user ID

    if (script.contains(pattern) || userName == user) {
        approveScript(pendingScript)
    }
}

println("Script approval process completed.")

