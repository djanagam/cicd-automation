// Iterate through all the nodes
Jenkins.instance.nodes.each { node ->
    def nodeName = node.getNodeName()
    def nodeLabel = node.getLabelString()
    
    // Get the total number of executors (workers) on each node
    def totalExecutors = node.getNumExecutors()
    
    // Calculate the number of busy and idle executors
    def busyExecutors = node.toComputer().countBusy()
    def idleExecutors = totalExecutors - busyExecutors

    // Print node name, label, total executors, busy executors, and idle executors
    println "Node Name: ${nodeName}"
    println "Node Label: ${nodeLabel}"
    println "Total Workers (Executors): ${totalExecutors}"
    println "Busy Workers (Executors): ${busyExecutors}"
    println "Idle Workers (Executors): ${idleExecutors}"
    println "=================================="
}