fetch("/api/data")
  .then((response) => response.json())
  .then((data) => {
    const products = data.data;

    // Populate category dropdown
    const categories = [...new Set(products.map((item) => item.category))];
    const categoryFilter = document.getElementById("categoryFilter");

    categories.forEach((category) => {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categoryFilter.appendChild(option);
    });

    // Populate website dropdown
    const websites = [...new Set(products.map((item) => item.website))];
    const websiteFilter = document.getElementById("websiteFilter");

    websites.forEach((website) => {
      const option = document.createElement("option");
      option.value = website;
      option.textContent = website;
      websiteFilter.appendChild(option);
    });

    // Function to render charts
    function renderCharts() {
      const selectedCategory = categoryFilter.value;
      const selectedWebsite = websiteFilter.value;
      const startDate = document.getElementById("startDate").value;
      const endDate = document.getElementById("endDate").value;

      // Filter data by category, website, and date range
      let filteredData = products;
      if (selectedCategory !== "all") {
        filteredData = filteredData.filter(
          (item) => item.category === selectedCategory
        );
      }
      if (selectedWebsite !== "all") {
        filteredData = filteredData.filter(
          (item) => item.website === selectedWebsite
        );
      }
      if (startDate) {
        filteredData = filteredData.filter(
          (item) => new Date(item.timestamp) >= new Date(startDate)
        );
      }
      if (endDate) {
        filteredData = filteredData.filter(
          (item) => new Date(item.timestamp) <= new Date(endDate)
        );
      }

      // Sort data by timestamp
      const sortedData = filteredData.sort(
        (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
      );

      // Prepare data for price chart
      const timestamps = sortedData.map((item) =>
        new Date(item.timestamp).toLocaleString()
      );
      const prices = sortedData.map((item) => item.price);

      // Prepare data for category chart
      const categoryAverages = categories.map((category) => {
        const categoryData = products.filter(
          (item) => item.category === category
        );
        const categoryPrices = categoryData.map((item) => item.price);
        const average =
          categoryPrices.length > 0
            ? categoryPrices.reduce((sum, price) => sum + price, 0) /
              categoryPrices.length
            : 0;
        return { category, average: average.toFixed(2) };
      });

      // Render price chart
      const priceChartCanvas = document.getElementById("priceChart");
      if (priceChartCanvas.chart) {
        priceChartCanvas.chart.destroy();
      }
      priceChartCanvas.chart = new Chart(priceChartCanvas, {
        type: "line",
        data: {
          labels: timestamps,
          datasets: [
            {
              label: "Preço ao longo do Tempo",
              data: prices,
              borderColor: "rgba(75, 192, 192, 1)",
              backgroundColor: "rgba(75, 192, 192, 0.2)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: "Data",
              },
              ticks: {
                autoSkip: true,
                maxTicksLimit: 20,
              },
            },
            y: {
              title: {
                display: true,
                text: "Preço (€)",
              },
            },
          },
        },
      });

      // Render category chart
      const categoryChartCanvas = document.getElementById("categoryChart");
      if (categoryChartCanvas.chart) {
        categoryChartCanvas.chart.destroy();
      }
      categoryChartCanvas.chart = new Chart(categoryChartCanvas, {
        type: "bar",
        data: {
          labels: categoryAverages.map((item) => item.category),
          datasets: [
            {
              label: "Preço Médio por Categoria",
              data: categoryAverages.map((item) => item.average),
              backgroundColor: "rgba(153, 102, 255, 0.2)",
              borderColor: "rgba(153, 102, 255, 1)",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: "Categoria",
              },
            },
            y: {
              title: {
                display: true,
                text: "Preço Médio (€)",
              },
            },
          },
        },
      });
    }

    // Add event listeners
    categoryFilter.addEventListener("change", renderCharts);
    websiteFilter.addEventListener("change", renderCharts);
    document.getElementById("startDate").addEventListener("change", renderCharts);
    document.getElementById("endDate").addEventListener("change", renderCharts);

    // Render charts on initial load
    renderCharts();
  })
  .catch((error) => console.error("Erro ao buscar dados:", error));