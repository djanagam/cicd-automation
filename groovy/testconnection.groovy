import java.net.*

// Define proxy settings
def proxyHost = "proxy.company.com"  // Replace with your proxy host
def proxyPort = 8080                 // Replace with your proxy port

// Define the external site to connect to
def targetUrl = "https://www.google.com"  // Replace with the URL you want to test

try {
    // Configure proxy
    Proxy proxy = new Proxy(Proxy.Type.HTTP, new InetSocketAddress(proxyHost, proxyPort))

    // Open connection to the external site
    URL url = new URL(targetUrl)
    HttpURLConnection connection = (HttpURLConnection) url.openConnection(proxy)

    // Set timeout values
    connection.setConnectTimeout(5000)
    connection.setReadTimeout(5000)

    // Send request
    connection.setRequestMethod("GET")
    connection.connect()

    // Check response code
    def responseCode = connection.getResponseCode()
    println "Connected to ${targetUrl} with response code: ${responseCode}"

    // Close connection
    connection.disconnect()
} catch (Exception e) {
    println "Failed to connect: ${e.message}"
}