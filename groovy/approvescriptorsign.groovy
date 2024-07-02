import org.jenkinsci.plugins.scriptsecurity.scripts.*

// Define the pattern to match
def pattern = /\/apps\/pipeline-worker\/work/

// Get the script approval instance
def scriptApproval = ScriptApproval.get()

// Approve pending scripts that match the pattern
def pendingScriptsToApprove = scriptApproval.pendingScripts.findAll { it.script =~ pattern }

pendingScriptsToApprove.each { pendingScript ->
    try {
        println "Approving script: ${pendingScript.hash} - ${pendingScript.script}"
        scriptApproval.approveScript(pendingScript.hash)
    } catch (Exception e) {
        println "Failed to approve script: ${pendingScript.hash} - ${e.message}"
    }
}

// Approve pending signatures that match the pattern
def pendingSignaturesToApprove = scriptApproval.pendingSignatures.findAll { it.signature =~ pattern }

pendingSignaturesToApprove.each { pendingSignature ->
    try {
        println "Approving signature: ${pendingSignature.signature}"
        scriptApproval.approveSignature(pendingSignature.signature)
    } catch (Exception e) {
        println "Failed to approve signature: ${pendingSignature.signature} - ${e.message}"
    }
}