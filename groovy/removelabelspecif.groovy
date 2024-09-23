// Groovy script to remove 'linuxrh8' label from all Jenkins nodes
def labelToRemove = "linuxrh8"

Jenkins.instance.nodes.each { node ->
    def labels = node.getLabelString().split()
    if (labels.contains(labelToRemove)) {
        def newLabels = labels.findAll { it != labelToRemove }.join(' ')
        node.setLabelString(newLabels)
        println("Updated labels for node '${node.displayName}': ${newLabels}")
    }
}