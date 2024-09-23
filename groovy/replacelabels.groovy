// Groovy script to replace the exact 'PrimaryLINUX' label with 'pipelineLINUX'
def labelToReplace = "PrimaryLINUX"
def newLabel = "pipelineLINUX"

Jenkins.instance.nodes.each { node ->
    def labels = node.getLabelString().split()
    if (labels.contains(labelToReplace)) {
        def updatedLabels = labels.collect { it == labelToReplace ? newLabel : it }.join(' ')
        node.setLabelString(updatedLabels)
        println("Updated labels for node '${node.displayName}': ${updatedLabels}")
    }
}