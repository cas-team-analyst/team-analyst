// Highcharts Global Defaults for Actuarial Applications
Highcharts.setOptions({
    // Global chart settings
    chart: {
        backgroundColor: '#ffffff',
        plotBorderWidth: null,
        plotShadow: false,
        style: {
            fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
    },

    // Title styling
    title: {
        style: {
            color: '#1f2937',
            fontSize: '18px',
            fontWeight: 'bold'
        }
    },

    // Subtitle styling
    subtitle: {
        style: {
            color: '#6b7280',
            fontSize: '14px'
        }
    },

    // Colors optimized for data visualization
    colors: [
        '#3b82f6', // blue-500
        '#ef4444', // red-500
        '#10b981', // emerald-500
        '#f59e0b', // amber-500
        '#8b5cf6', // violet-500
        '#06b6d4', // cyan-500
        '#84cc16', // lime-500
        '#f97316', // orange-500
        '#ec4899', // pink-500
        '#6366f1'  // indigo-500
    ],

    // Legend settings
    legend: {
        itemStyle: {
            color: '#374151',
            fontSize: '12px'
        },
        itemHoverStyle: {
            color: '#1f2937'
        },
        itemHiddenStyle: {
            color: '#9ca3af'
        }
    },

    // X-axis defaults
    xAxis: {
        gridLineColor: '#e5e7eb',
        gridLineWidth: 1,
        lineColor: '#d1d5db',
        tickColor: '#d1d5db',
        endOnTick: true,
        startOnTick: true,
        labels: {
            style: {
                color: '#6b7280',
                fontSize: '11px'
            }
        },
        title: {
            style: {
                color: '#374151',
                fontSize: '12px',
                fontWeight: '600'
            }
        }
    },

    // Y-axis defaults
    yAxis: {
        gridLineColor: '#e5e7eb',
        lineColor: '#d1d5db',
        tickColor: '#d1d5db',
        endOnTick: true,
        startOnTick: true,
        labels: {
            style: {
                color: '#6b7280',
                fontSize: '11px'
            }
        },
        title: {
            style: {
                color: '#374151',
                fontSize: '12px',
                fontWeight: '600'
            }
        }
    },

    // Tooltip defaults
    tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        style: {
            color: 'white',
            fontSize: '12px'
        },
        borderWidth: 0,
        borderRadius: 4
    },

    // Plot options for common chart types
    plotOptions: {
        line: {
            dataLabels: {
                color: '#374151',
                style: {
                    fontSize: '10px',
                    textOutline: 'none'
                }
            },
            marker: {
                lineColor: '#ffffff',
                lineWidth: 2
            }
        },
        column: {
            dataLabels: {
                color: '#374151',
                style: {
                    fontSize: '10px',
                    textOutline: 'none'
                }
            }
        },
        bar: {
            dataLabels: {
                color: '#374151',
                style: {
                    fontSize: '10px',
                    textOutline: 'none'
                }
            }
        },
        series: {
            animation: {
                duration: 1000
            }
        }
    },

    // Credits
    credits: {
        enabled: false
    },

    // Exporting options
    exporting: {
        enabled: false
    },

    // Responsive options
    responsive: {
        rules: [{
            condition: {
                maxWidth: 640
            },
            chartOptions: {
                legend: {
                    layout: 'horizontal',
                    align: 'center',
                    verticalAlign: 'bottom'
                }
            }
        }]
    }
});

// Utility functions for common actuarial chart configurations
window.ActuarialCharts = {
    // Loss development pattern chart
    lossTriangle: function (container, data, options = {}) {
        return Highcharts.chart(container, Highcharts.merge({
            chart: {
                type: 'line'
            },
            title: {
                text: options.title || 'Loss Development Pattern'
            },
            xAxis: {
                title: {
                    text: 'Development Period'
                },
                categories: options.categories || []
            },
            yAxis: {
                title: {
                    text: 'Cumulative Loss Ratio'
                },
                labels: {
                    formatter: function () {
                        return this.value.toFixed(3);
                    }
                }
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        'Period ' + this.x + ': ' + this.y.toFixed(4);
                }
            },
            series: data
        }, options));
    },

    // Development factors chart
    developmentFactors: function (container, data, options = {}) {
        return Highcharts.chart(container, Highcharts.merge({
            chart: {
                type: 'column'
            },
            title: {
                text: options.title || 'Age-to-Age Development Factors'
            },
            xAxis: {
                title: {
                    text: 'Development Period'
                },
                categories: options.categories || []
            },
            yAxis: {
                title: {
                    text: 'Development Factor'
                },
                labels: {
                    formatter: function () {
                        return this.value.toFixed(3);
                    }
                }
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        this.x + ': ' + this.y.toFixed(4);
                }
            },
            series: data
        }, options));
    }
};