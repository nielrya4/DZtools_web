from lib.objects.graphs import KDE, MDS, PDP, CDF
from lib.utils.files import generate_matrix
from lib.utils import unmixing_utils


def run(script_file, samples):
    items = []
    lines = open(script_file).read().split("\n")
    active_samples = samples.copy()

    commands = ["kde", "pdp", "cdf", "mds", "sim",
                "dis", "lik", "ks", "kpr", "ccr",
                "load", "purge", "stacked", "unstacked",
                "unmix"]
    bandwidth = 10

    stacked = False

    for line in lines:
        cmd = __get_cmd(line)
        args = __get_args(line)
        adjusted_samples = [sample.replace_bandwidth(bandwidth) for sample in active_samples]
        row_labels = [sample.name for sample in active_samples]
        col_labels = [sample.name for sample in active_samples]

        if cmd in commands:
            if cmd == "kde":
                items.append(KDE(adjusted_samples, "Kernel Density Estimate", stacked=stacked).plot())
            elif cmd == "pdp":
                items.append(PDP(active_samples, "Probability Density Plot", stacked=stacked).plot())
            elif cmd == "cdf":
                items.append(CDF(active_samples, "Cumulative Distribution Function").plot())
            elif cmd == "mds":
                items.append(MDS(active_samples, "Multidimensional Scaling Plot").plot())
            elif cmd == "unmix":
                data1, _, _ = unmixing_utils.do_monte_carlo(active_samples, num_trials=1000)
                items.append(data1)
            elif cmd == "sim":
                header = "<h5>Similarity Matrix</h5>"
                items.append(header + generate_matrix(adjusted_samples,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="similarity").to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">'))
            elif cmd == "dis":
                header = "<h5>Dissimilarity Matrix</h5>"
                items.append(header + generate_matrix(adjusted_samples,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="dissimilarity").to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">'))
            elif cmd == "lik":
                header = "<h5>Likeness Matrix</h5>"
                items.append(header + generate_matrix(adjusted_samples,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="likeness").to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">'))
            elif cmd == "ks":
                header = "<h5>KS Test Matrix</h5>"
                items.append(header + generate_matrix(adjusted_samples,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="ks").to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">'))
            elif cmd == "kpr":
                header = "<h5>Kuiper Test Matrix</h5>"
                items.append(header + generate_matrix(adjusted_samples,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="kuiper").to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">'))
            elif cmd == "ccr":
                header = "<h5>Cross-Correlation Matrix</h5>"
                items.append(header + generate_matrix(adjusted_samples,
                                            row_labels=row_labels,
                                            col_labels=col_labels,
                                            matrix_type="cross_correlation").to_html(classes="table table-bordered table-striped", justify="center").replace('<th>','<th style = "background-color: White;">').replace('<td>','<td style = "background-color: White;">'))
            elif cmd == "stacked":
                stacked = True
            elif cmd == "unstacked":
                stacked = False
            elif cmd == "load":
                if args:
                    for arg in args:
                        if arg == "all":
                            active_samples = samples.copy()
                        elif arg in [sample.name for sample in samples] and arg not in [active_sample.name for active_sample in active_samples]:
                            for sample in samples:
                                if arg == sample.name:
                                    active_samples.append(sample)
                else:
                    active_samples = samples.copy()
            elif cmd == "purge":
                if args:
                    for arg in args:
                        if arg == "all":
                            active_samples = []
                        elif arg in [active_sample.name for active_sample in active_samples]:
                            for sample in active_samples:
                                if arg == sample.name:
                                    active_samples.remove(sample)
                else:
                    active_samples = []
            else:
                items.append(f"<p>Command {cmd} not recognized</p>")
    return items


def __get_args(line):
    arg_start_index = 0
    if "$" in line:
        for i, char in enumerate(line):
            if char == "$":
                arg_start_index = i
                break
        args = [arg.strip() for arg in line[arg_start_index:].split("$") if arg.strip()]
    else:
        args = ""
    return args


def __get_cmd(line):
    arg_start_index = 0
    if "$" in line:
        for i, char in enumerate(line):
            if char == "$":
                arg_start_index = i
                break
        cmd = line[:arg_start_index].strip()
    else:
        cmd = line.strip()
    return cmd
