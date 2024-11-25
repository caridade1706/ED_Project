fetch("/api/data")
  .then((response) => response.json())
  .then((data) => {
    const products = data.data;
    
    // Function to render charts
    function renderCharts() {

      const categories = [...new Set(products.map((item) => item.category))];

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
              label: "Average Price per Category",
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

    // Render charts on initial load
    renderCharts();
  })
  .catch((error) => console.error("Erro ao buscar dados:", error));