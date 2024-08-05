You can send metrics directly from GitHub Enterprise Server (GHES) to Prometheus without needing Collectd in the middle. This can simplify your setup. GHES natively supports exporting metrics in a format that Prometheus can scrape. Here's how you can achieve this:

### Direct Metrics Export from GitHub to Prometheus

#### Step 1: Enable Prometheus Metrics on GitHub Enterprise Server

1. **SSH into your GitHub Enterprise Server:**
   ```bash
   ssh admin@your-github-enterprise-server
   ```

2. **Enable Prometheus metrics:**
   ```bash
   ghe-config app.prometheus.enabled true
   ghe-config app.prometheus.listen_address 0.0.0.0:9090
   ghe-config save
   ```

3. **Restart GitHub Enterprise services to apply the changes:**
   ```bash
   ghe-service-restart
   ```

#### Step 2: Configure Prometheus to Scrape GitHub Metrics

1. **Edit your Prometheus configuration file (`prometheus.yml`):**
   ```yaml
   scrape_configs:
     - job_name: 'github_enterprise'
       static_configs:
         - targets: ['<GHE_HOSTNAME>:9090']
   ```
   Replace `<GHE_HOSTNAME>` with the actual hostname or IP address of your GitHub Enterprise Server.

2. **Restart Prometheus to apply the new configuration:**
   ```bash
   systemctl restart prometheus
   ```

#### Step 3: Visualize Metrics in Grafana

1. **Add Prometheus as a Data Source in Grafana:**
   - Navigate to Grafana in your web browser.
   - Go to **Configuration** -> **Data Sources** -> **Add data source**.
   - Select **Prometheus** and enter the URL of your Prometheus server (e.g., `http://localhost:9090`).
   - Click **Save & Test**.

2. **Create Dashboards in Grafana:**
   - Use the Grafana UI to create dashboards and panels that query metrics from Prometheus.

### Summary

By enabling Prometheus metrics on your GitHub Enterprise Server and configuring Prometheus to scrape these metrics directly, you eliminate the need for Collectd in your monitoring setup. Prometheus handles the collection and storage of metrics, while Grafana provides the visualization.

This setup simplifies the architecture and reduces the number of components you need to manage, making it easier to maintain and troubleshoot.

If you have specific requirements or need further assistance with configuration, feel free to ask!