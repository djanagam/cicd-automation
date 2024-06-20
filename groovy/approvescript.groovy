import org.jenkinsci.plugins.scriptsecurity.scripts.*

// Define the pattern to match
def pattern = /\/apps\/pipeline-worker\/work/

// Get the script approval instance
def scriptApproval = ScriptApproval.get()

// Approve pending scripts that match the pattern
scriptApproval.pendingScripts.each { pendingScript ->
    if (pendingScript.script =~ pattern) {
        println "Approving script: ${pendingScript.hash} - ${pendingScript.script}"
        scriptApproval.approveScript(pendingScript.hash)
    }
}

// Approve pending signatures that match the pattern
scriptApproval.pendingSignatures.each { pendingSignature ->
    if (pendingSignature.signature =~ pattern) {
        println "Approving signature: ${pendingSignature.signature}"
        scriptApproval.approveSignature(pendingSignature.signature)
    }
}