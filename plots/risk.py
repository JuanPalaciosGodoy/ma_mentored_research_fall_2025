import matplotlib.pyplot as plt
import numpy as np

def plot_coverage_comparison(results:dict):

    fig, axes = plt.subplots(1, 3, figsize=(25,12))
    colors = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6', '#f1c40f', '#2ecc71', '#ecf0f1']

    methods = list(results.keys())

    coverages = [results[m].coverage for m in methods]
    widths = [results[m].avg_interval_width for m in methods]
    violations = [results[m].violations for m in methods]

    # plot coverage
    ax1 = axes[0]
    bars1 = ax1.bar(range(len(methods)), coverages, color=colors, alpha=0.8, edgecolor='black')
    ax1.axhline(y=0.95, color='green', linestyle='--', linewidth=2, label='Target Coverage (95%)')
    ax1.set_xticks(range(len(methods)))
    ax1.set_xticklabels(methods, rotation=45, ha='right', fontsize=9)
    ax1.set_ylabel('Coverage Rate', fontsize=11)
    ax1.set_title('Coverage Comparison', fontsize=12, fontweight='bold')
    ax1.set_ylim(0.75, 1.0)
    ax1.legend(loc='lower right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3)

    # add value labels
    for bar, cov in zip(bars1, coverages):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f'{cov:.1%}', ha='center', va='bottom', fontsize=8)

    # Plot interval width
    ax2 = axes[1]
    bars2 = ax2.bar(range(len(methods)), widths, color=colors, alpha = 0.8, edgecolor='black')
    ax2.set_xticks(range(len(methods)))
    ax2.set_xticklabels(methods, rotation=45, ha='right', fontsize=9)
    ax2.set_ylabel('Average Interval Width', fontsize=11)
    ax2.set_title('Interval Width (Efficiency)', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)


    # plot violations
    ax3 = axes[2]
    expected_violations = 0.05 * results['Historical VaR'].total_observations
    bars3 = ax3.bar(range(len(methods)), violations, color=colors, alpha=0.8, edgecolor='black')
    ax3.axhline(y=expected_violations, color='green', linestyle='--', linewidth=2, label=f'Expected ({expected_violations:.0f})')
    ax3.set_xticks(range(len(methods)))
    ax3.set_xticklabels(methods, rotation=45, ha='right', fontsize=9)
    ax3.set_ylabel('Number of Violations', fontsize=11)
    ax3.set_title('Violation Count', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=9)
    ax3.grid(axis='y', alpha=0.3)

    plt.suptitle('Conformal Prediction vs Classical VaR: Risk Measurement Comparison', fontsize=14, fontweight='bold', y=1.02)
    plt.show()


def plot_rolling_statistics(results:dict, details:dict, window:int=50):

    fig, axes = plt.subplots(2, 2, figsize=(25,18))
    colors = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6', '#f1c40f', '#2ecc71', '#ecf0f1']

    methods = list(results.keys())

    ax1 = axes[0, 0]
    for method, color in zip(methods, colors):
        df = details[method]
        rolling_cov = (~df['violation']).rolling(window=window).mean()
        ax1.plot(df['time'], rolling_cov, label=method, color=color, linewidth=1.5)

    ax1.axhline(y=0.95, color='green', linestyle='--', linewidth=2, label='Target Coverage (95%)')
    ax1.set_xlabel('Time', fontsize=11)
    ax1.set_ylabel('Rolling Coverage', fontsize=11)
    ax1.set_title(f'Rolling Coverage (window = {window})', fontsize=12, fontweight='bold')
    ax1.set_ylim(0.7, 1.05)
    ax1.legend(loc='lower right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3)

    # rolling interval width
    ax2 = axes[0, 1]
    for method, color in zip(methods, colors):
        df = details[method]
        rolling_width = df['interval_width'].rolling(window=window).mean()
        ax2.plot(df['time'], rolling_width, label=method, color=color, linewidth=1.5)

    ax2.axhline(y=0.95, color='green', linestyle='--', linewidth=2, label='Target Coverage (95%)')
    ax2.set_xlabel('Time', fontsize=11)
    ax2.set_ylabel('Rolling Average Interval Width', fontsize=11)
    ax2.set_title(f'Rolling Interval Width (window = {window})', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(axis='y', alpha=0.3)

    # expected violations line
    ax3 = axes[1, 0]
    for method, color in zip(methods, colors):
        df = details[method]
        cum_violations = df['violation'].cumsum()
        ax3.plot(df['time'], cum_violations, label=method, color=color, linewidth=1.5)


    expected_line = 0.05 * np.arange(1, len(details['Historical VaR']) + 1)
    ax3.plot(details['Historical VaR']['time'], expected_line, 'g--', linewidth=2, label='Expected (5%)')
    ax3.set_xlabel('Time', fontsize=11)
    ax3.set_ylabel('Cumulative Violations', fontsize=11)
    ax3.set_title(f'Cumulative Violations Over Time', fontsize=12, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(alpha=0.3)

    # Efficiency Frontier (Coverage vs Width)
    ax4 = axes[1, 1]
    for method, color in zip(methods, colors):
        result = results[method]
        rolling_width = df['interval_width'].rolling(window=window).mean()
        ax4.scatter(result.avg_interval_width, result.coverage, s=150, label=method, color=color, linewidth=1.5, alpha=0.8)

    ax4.axhline(y=0.95, color='green', linestyle='--', linewidth=2, alpha=0.7)
    ax4.set_xlabel('Average Interval Width (Efficiency)', fontsize=11)
    ax4.set_ylabel('Coverage Rate (Validity)', fontsize=11)
    ax4.set_title(f'Efficiency Validity Trade-off', fontsize=12, fontweight='bold')
    ax4.legend(loc='lower right', fontsize=8)
    ax4.grid(alpha=0.3)

    # add annotation on ideal region
    ax4.annotate('Ideal Region\n(High Coverage, \nNarrow Intervals)', xy=(0.15, 0.96), fontsize=9, ha='center', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

    plt.suptitle('Conformal Prediction vs VaR: Detailed Analysis', fontsize=14, fontweight='bold', y=1.01)
    plt.show()


def plot_prediction_intervals(results:dict, details:dict):

    fig, axes = plt.subplots(3,2,figsize=(25,18))
    methods = list(results.keys())

    for idx, method in enumerate(methods):
        ax = axes[idx // 2, idx % 2]
        df = details[method]

        # Plot actual returns
        ax.plot(df['time'], df['actual'], 'k-', linewidth=0.5, alpha=0.7, label='Actual Returns')

        # Plot Prediction interval
        ax.fill_between(df['time'], df['lower'], df['upper'], alpha=0.3, color='blue' if 'Conformal' in method or method == 'ACI' else 'red', label = 'Prediction Interval')

        # mark breaches
        violations_df = df[df['violation']==True]
        ax.scatter(violations_df['time'], violations_df['actual'], color='red', s=20, zorder=5, label=f'Violations ({len(violations_df)})')

        ax.set_title(f'{method}\nCoverage: {results[method].coverage:.1%}, '
                    f'Average Width: {results[method].avg_interval_width:.4f}',
                    fontsize=11, fontweight='bold')

        ax.set_xlabel('Time', fontsize=10)
        ax.set_ylabel('Return', fontsize=10)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(alpha=0.3)

    plt.suptitle('Prediction Intervals Over Time: Conformal vs VaR Methods \n', fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.show()