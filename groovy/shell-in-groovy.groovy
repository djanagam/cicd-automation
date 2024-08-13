def script = '''
#!/bin/bash
echo "This is a test shell script."
echo "Current directory: $(pwd)"
echo "Listing files:"
ls -l
'''

// Execute the script
def process = ['bash', '-c', script].execute()

// Capture the output of the shell script
def output = new StringBuilder()
process.inputStream.eachLine { line ->
    output.append(line).append("\n")
}

// Wait for the process to complete
process.waitFor()

// Print the output and the exit value
println "Output:\n${output.toString()}"
println "Exit value: ${process.exitValue()}"

if (process.exitValue() != 0) {
    println "Script execution failed."
} else {
    println "Script executed successfully."
}