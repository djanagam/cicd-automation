// Print the header row in CSV format
println "Node Name,Node Label,Total Workers (Executors),Busy Workers (Executors),Idle Workers (Executors)"

// Iterate through all the nodes
Jenkins.instance.nodes.each { node ->
    def nodeName = node.getNodeName()
    def nodeLabel = node.getLabelString()
    
    // Get the total number of executors (workers) on each node
    def totalExecutors = node.getNumExecutors()
    
    // Calculate the number of busy and idle executors
    def busyExecutors = node.toComputer().countBusy()
    def idleExecutors = totalExecutors - busyExecutors

    // Print data in CSV format
    println "${nodeName},${nodeLabel},${totalExecutors},${busyExecutors},${idleExecutors}"
}