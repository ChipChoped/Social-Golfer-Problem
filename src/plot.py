import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.collections import PathCollection


def plot_commun(fig: plt.Figure, ax: plt.Axes, df: pd.DataFrame, timeout: int,
                scatter: PathCollection, title: str = None):
    plt.colorbar(scatter, label="Nombre de groupes")

    handles, labels = scatter.legend_elements(prop="sizes", alpha=0.6,
                                              num=df["participants"].max() + 1)
    labels = range(1, df["participants"].max() + 1)
    ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(1.2, 1), borderaxespad=0,
              title="Nombre de\nparticipants")

    if title is not None:
        title = ax.set_title(title)

        title.set_y(1.05)
        fig.subplots_adjust(top=0.85)


def plot_instances_by_time(df: pd.DataFrame, timeout: int, title: str = None):
    fig: plt.Figure
    ax: plt.Axes

    fig, ax = plt.subplots(figsize=(10, 5))

    scatter = ax.scatter(x=df["weeks"], y=df["time"], c=df["groups"],
                         s=(np.power(2, df["participants"] * 1.2) + 50),
                         cmap="rainbow", alpha=0.5)

    plt.xlabel("Nombre de semaines")
    plt.ylabel("Temps de résolution (s)")

    plt.plot(np.repeat(timeout, df.shape[1]), color="black", linestyle='dotted')
    plt.text(0, timeout - 0.25, 'Timeout')

    plot_commun(fig, ax, df, timeout, scatter, title)


def plot_instances_by_n_solutions_found(df: pd.DataFrame, timeout: int, title: str = None):
    fig: plt.Figure
    ax: plt.Axes

    fig, ax = plt.subplots(figsize=(10, 5))

    scatter = ax.scatter(x=df["weeks"], y=df["n_solutions_found"], c=df["groups"],
                         s=(np.power(2, df["participants"] * 1.2) + 50),
                         cmap="rainbow", alpha=0.5)

    plt.xlabel("Nombre de semaines")
    plt.ylabel("Nombre de solutions trouvées")

    plot_commun(fig, ax, df, timeout, scatter, title)


def plot_solution_loss_by_model(df: pd.DataFrame, timeout: int, title: str = None):
    fig: plt.Figure
    ax: plt.Axes

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = ['blue', 'violet', 'red']

    no_sym_all = df[(~df["symmetry_breaking"]) & (df["all_solutions"]) & (df["weeks"] >= 3)]
    no_sym_all_1 = no_sym_all[no_sym_all["model"] == 1]
    no_sym_all_2 = no_sym_all[no_sym_all["model"] == 2]
    no_sym_all_3 = no_sym_all[no_sym_all["model"] == 3]

    x: list = []
    y: list = []

    for i in range(2, df["weeks"].max()):
        x += ["M1\nW" + str(i + 1), "M2\nW" + str(i + 1), "M3\nW" + str(i + 1)]
        y += [round(no_sym_all_1[no_sym_all_1["weeks"] == i + 1]["n_solutions_found"].mean()),
              round(no_sym_all_2[no_sym_all_2["weeks"] == i + 1]["n_solutions_found"].mean()),
              round(no_sym_all_3[no_sym_all_3["weeks"] == i + 1]["n_solutions_found"].mean())]

    bar = ax.bar(x, y, color=colors)

    for i in range(len(x)):
        plt.text(i, y[i] // 2, y[i], ha='center',
                 bbox=dict(facecolor='white', alpha=.8))

    plt.xlabel("Modèle")
    plt.ylabel("Nombre de solutions trouvées")

    if title is not None:
        title = ax.set_title(title)

        title.set_y(1.05)
        fig.subplots_adjust(bottom=0.15)


def plot_solution_loss_by_symmetry(df: pd.DataFrame, timeout: int, title: str = None):
    fig: plt.Figure
    ax: plt.Axes

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = ['blue', 'violet', 'red']

    no_sym_all = df[(~df["symmetry_breaking"]) & (df["all_solutions"]) & (df["weeks"] >= 3)]
    no_sym_all_1 = no_sym_all[no_sym_all["model"] == 1]
    no_sym_all_2 = no_sym_all[no_sym_all["model"] == 2]
    no_sym_all_3 = no_sym_all[no_sym_all["model"] == 3]

    sym_all = df[(df["symmetry_breaking"]) & (df["all_solutions"]) & (df["weeks"] >= 3)]
    sym_all_1 = sym_all[sym_all["model"] == 1]
    sym_all_2 = sym_all[sym_all["model"] == 2]
    sym_all_3 = sym_all[sym_all["model"] == 3]

    x: list = ["Modèle 1\nSans symétrie", "Modèle 2\nSans symétrie", "Modèle 3\nSans symétrie",
               "Modèle 1\nAvec symétrie", "Modèle 2\nAvec symétrie", "Modèle 3\nAvec symétrie"]
    y: list = [round(no_sym_all_1["n_solutions_found"].mean()), round(no_sym_all_2["n_solutions_found"].mean()),
               round(no_sym_all_3["n_solutions_found"].mean()), round(sym_all_1["n_solutions_found"].mean()),
               round(sym_all_2["n_solutions_found"].mean()), round(sym_all_3["n_solutions_found"].mean())]

    bar1 = ax.bar(x, y, color=colors)

    for i in range(len(x)):
        plt.text(i, y[i] // 2, y[i], ha='center',
                 bbox=dict(facecolor='white', alpha=.8))

    plt.xlabel("Modèle")
    plt.ylabel("Nombre de solutions trouvées")

    if title is not None:
        title = ax.set_title(title)

        title.set_y(1.05)
        fig.subplots_adjust(bottom=0.18)


def plot_time_by_model(df: pd.DataFrame, dfs: pd.DataFrame, timeout: int, title: str = None):
    fig: plt.Figure
    ax: plt.Axes

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = ['blue', 'violet', 'red', 'blue', 'violet', 'red', 'darkviolet']

    no_sym = df[(~df["symmetry_breaking"]) & (~df["all_solutions"]) & (~df["timed_out"])]
    no_sym_1 = no_sym[no_sym["model"] == 1]
    no_sym_2 = no_sym[no_sym["model"] == 2]
    no_sym_3 = no_sym[no_sym["model"] == 3]

    sym = df[(df["symmetry_breaking"]) & (~df["all_solutions"])]
    sym_1 = sym[sym["model"] == 1]
    sym_2 = sym[sym["model"] == 2]
    sym_3 = sym[sym["model"] == 3]

    x: list = ["Modèle 1\nSans symétrie", "Modèle 2\nSans symétrie", "Modèle 3\nSans symétrie",
               "Modèle 1\nAvec symétrie", "Modèle 2\nAvec symétrie", "Modèle 3\nAvec symétrie",
               "Solver"]
    y: list = [round(no_sym_1["time"].mean(), 3), round(no_sym_2["time"].mean(), 3), round(no_sym_3["time"].mean(), 3),
               round(sym_1["time"].mean(), 3), round(sym_2["time"].mean(), 3), round(sym_3["time"].mean(), 3),
               round(dfs["time"].mean(), 3)]

    bar1 = ax.bar(x, y, color=colors)

    for i in range(len(x)):
        plt.text(i, y[i] // 2, y[i], ha='center',
                 bbox=dict(facecolor='white', alpha=.8))

    plt.xlabel("Modèle")
    plt.ylabel("Temps de résolution (s)")

    if title is not None:
        title = ax.set_title(title)

        title.set_y(1.05)
        fig.subplots_adjust(bottom=0.18)


def plot_found_solution_by_model(df: pd.DataFrame, dfs: pd.DataFrame, timeout: int, title: str = None):
    fig: plt.Figure
    ax: plt.Axes

    fig, ax = plt.subplots(figsize=(10, 5))

    colors = ['blue', 'violet', 'red', 'blue', 'violet', 'red', 'darkviolet']

    no_sym = df[(~df["symmetry_breaking"]) & (~df["all_solutions"]) & (~df["timed_out"])]
    no_sym_1 = no_sym[no_sym["model"] == 1]
    no_sym_2 = no_sym[no_sym["model"] == 2]
    no_sym_3 = no_sym[no_sym["model"] == 3]

    sym = df[(df["symmetry_breaking"]) & (~df["all_solutions"])]
    sym_1 = sym[sym["model"] == 1]
    sym_2 = sym[sym["model"] == 2]
    sym_3 = sym[sym["model"] == 3]

    x: list = ["Modèle 1\nSans symétrie", "Modèle 2\nSans symétrie", "Modèle 3\nSans symétrie",
               "Modèle 1\nAvec symétrie", "Modèle 2\nAvec symétrie", "Modèle 3\nAvec symétrie",
               "Solver"]
    y: list = [no_sym_1.shape[0], no_sym_2.shape[0], no_sym_3.shape[0],
               sym_1.shape[0], sym_2.shape[0], sym_3.shape[0],
               dfs.shape[0]]

    bar1 = ax.bar(x, y, color=colors)

    for i in range(len(x)):
        plt.text(i, y[i] // 2, y[i], ha='center',
                 bbox=dict(facecolor='white', alpha=.8))

    plt.xlabel("Modèle")
    plt.ylabel("Temps de résolution (s)")

    if title is not None:
        title = ax.set_title(title)

        title.set_y(1.05)
        fig.subplots_adjust(bottom=0.18)


def main(file_path_1: str, file_path_2):
    if not file_path_1.lower().endswith('.csv') and not file_path_2.lower().endswith('.csv'):
        print("The files must be CSV files")
        exit(1)

    index: int = file_path_1.find("w_")
    timeout_search: bool = True
    multiplier: int = 1
    timeout: int = 0

    while timeout_search:
        if file_path_1[index + 2].isdigit():
            timeout = timeout * multiplier + int(file_path_1[index + 2])
            multiplier *= 10
            index += 1
        else:
            timeout_search = False

    instances = pd.read_csv(file_path_1)
    instances = instances.dropna()

    solver = pd.read_csv(file_path_2)
    solver = solver.dropna()

    solver_no_fail = solver[solver["solution"] | solver["timed_out"]]
    test = solver[solver["solution"] != solver["valid"]]

    no_fail = instances[instances["n_solutions_found"] != 0 | instances["timed_out"]]

    one_solution = no_fail[~no_fail["all_solutions"]]
    one_solution_sym = one_solution[one_solution["symmetry_breaking"]]
    one_solution_no_sym = one_solution[~one_solution["symmetry_breaking"]]

    all_solutions = no_fail[no_fail["all_solutions"]]
    all_solutions_sym = all_solutions[all_solutions["symmetry_breaking"]]
    all_solutions_no_sym = all_solutions[~all_solutions["symmetry_breaking"]]

    Path("../plot").mkdir(parents=True, exist_ok=True)
    Path("../plot/time").mkdir(parents=True, exist_ok=True)
    Path("../plot/solutions").mkdir(parents=True, exist_ok=True)

    # plot_instances_by_time(one_solution_no_sym, timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\n sans bris de symétrie et avec une seule solution")
    # plt.savefig("../plot/time/one_solution_no_sym.png")
    #
    # plot_instances_by_time(one_solution_no_sym[one_solution_no_sym["model"] == 1], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\nsans bris de symétrie et avec une seule solution"
    #                        "\npour le modèle 1")
    # plt.savefig("../plot/time/one_solution_no_sym_model_1.png")
    #
    # plot_instances_by_time(one_solution_no_sym[one_solution_no_sym["model"] == 2], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\nsans bris de symétrie et avec une seule solution"
    #                        "\npour le modèle 2")
    # plt.savefig("../plot/time/one_solution_no_sym_model_2.png")
    #
    # plot_instances_by_time(one_solution_no_sym[one_solution_no_sym["model"] == 3], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\nsans bris de symétrie et avec une seule solution"
    #                        "\npour le modèle 3")
    # plt.savefig("../plot/time/one_solution_no_sym_model_3.png")
    #
    # plot_instances_by_time(one_solution_sym, timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec une seule solution")
    # plt.savefig("../plot/time/one_solution_sym.png")
    #
    # plot_instances_by_time(one_solution_sym[one_solution_sym["model"] == 1], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec une seule solution"
    #                        "\npour le modèle 1")
    # plt.savefig("../plot/time/one_solution_sym_model_1.png")
    #
    # plot_instances_by_time(one_solution_sym[one_solution_sym["model"] == 2], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec une seule solution"
    #                        "\npour le modèle 2")
    # plt.savefig("../plot/time/one_solution_sym_model_2.png")
    #
    # plot_instances_by_time(one_solution_sym[one_solution_sym["model"] == 3], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec une seule solution"
    #                        "\npour le modèle 3")
    # plt.savefig("../plot/time/one_solution_sym_model_3.png")
    #
    # plot_instances_by_time(all_solutions_no_sym, timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\n sans bris de symétrie et avec toutes les solutions")
    # plt.savefig("../plot/time/all_solutions_no_sym.png")
    #
    # plot_instances_by_time(all_solutions_no_sym[all_solutions_no_sym["model"] == 1], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\nsans bris de symétrie et avec toutes les solutions"
    #                        "\npour le modèle 1")
    # plt.savefig("../plot/time/all_solutions_no_sym_model_1.png")
    #
    # plot_instances_by_time(all_solutions_no_sym[all_solutions_no_sym["model"] == 2], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\nsans bris de symétrie et avec toutes les solutions"
    #                        "\npour le modèle 2")
    # plt.savefig("../plot/time/all_solutions_no_sym_model_2.png")
    #
    # plot_instances_by_time(all_solutions_no_sym[all_solutions_no_sym["model"] == 3], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\nsans bris de symétrie et avec toutes les solutions"
    #                        "\npour le modèle 3")
    # plt.savefig("../plot/time/all_solutions_no_sym_model_3.png")
    #
    # plot_instances_by_time(all_solutions_sym, timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec toutes les solutions")
    # plt.savefig("../plot/time/all_solutions_sym.png")
    #
    # plot_instances_by_time(all_solutions_sym[all_solutions_sym["model"] == 1], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec toutes les solutions"
    #                        "\npour le modèle 1")
    # plt.savefig("../plot/time/all_solutions_sym_model_1.png")
    #
    # plot_instances_by_time(all_solutions_sym[all_solutions_sym["model"] == 2], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec toutes les solutions"
    #                        "\npour le modèle 2")
    # plt.savefig("../plot/time/all_solutions_sym_model_2.png")
    #
    # plot_instances_by_time(all_solutions_sym[all_solutions_sym["model"] == 3], timeout,
    #                        "Temps de résolution pour des instances du SGP" +
    #                        "\navec bris de symétrie et avec toutes les solutions"
    #                        "\npour le modèle 3")
    # plt.savefig("../plot/time/all_solutions_sym_model_3.png")
    #
    # plot_instances_by_n_solutions_found(all_solutions_no_sym, timeout,
    #                                     "Nombre de solutions trouvées pour des instances du SGP" +
    #                                     "\nsans bris de symétrie")
    # plt.savefig("../plot/solutions/all_solutions_no_sym.png")
    #
    # plot_instances_by_n_solutions_found(all_solutions_no_sym[all_solutions_no_sym["model"] == 1], timeout,
    #                                     "Nombre de solutions trouvées pour des instances du SGP" +
    #                                     "\nsans bris de symétrie"
    #                                     "\npour le modèle 1")
    # plt.savefig("../plot/solutions/all_solutions_no_sym_model_1.png")
    #
    # plot_instances_by_n_solutions_found(all_solutions_no_sym[all_solutions_no_sym["model"] == 2], timeout,
    #                                     "Nombre de solutions trouvées pour des instances du SGP" +
    #                                     "\nsans bris de symétrie"
    #                                     "\npour le modèle 2")
    # plt.savefig("../plot/solutions/all_solutions_no_sym_model_2.png")
    #
    # plot_instances_by_n_solutions_found(all_solutions_no_sym[all_solutions_no_sym["model"] == 3], timeout,
    #                                     "Nombre de solutions trouvées pour des instances du SGP" +
    #                                     "\nsans bris de symétrie"
    #                                     "\npour le modèle 3")
    # plt.savefig("../plot/solutions/all_solutions_no_sym_model_3.png")
    #
    # plot_instances_by_n_solutions_found(all_solutions_sym, timeout,
    #                                     "Nombre de solutions trouvées pour des instances du SGP" +
    #                                     "\navec bris de symétrie")
    # plt.savefig("../plot/solutions/all_solutions_sym.png")
    #
    # plot_instances_by_n_solutions_found(all_solutions_sym[all_solutions_sym["model"] == 1], timeout,
    #                                     "Nombre de solutions trouvées pour des instances du SGP" +
    #                                     "\navec bris de symétrie"
    #                                     "\npour le modèle 1")
    # plt.savefig("../plot/solutions/all_solutions_sym_model_1.png")
    #
    # plot_instances_by_n_solutions_found(all_solutions_sym[all_solutions_sym["model"] == 2], timeout,
    #                                     "Nombre de solutions trouvées pour des instances du SGP" +
    #                                     "\navec bris de symétrie"
    #                                     "\npour le modèle 2")
    # plt.savefig("../plot/solutions/all_solutions_sym_model_2.png")

    plot_instances_by_n_solutions_found(all_solutions_sym[all_solutions_sym["model"] == 3], timeout,
                                        "Nombre de solutions trouvées pour des instances du SGP" +
                                        "\navec bris de symétrie"
                                        "\npour le modèle 3")
    plt.savefig("../plot/solutions/all_solutions_sym_model_3.png")

    plot_solution_loss_by_model(no_fail, timeout,
                                "Comparaison du nombre de solutions entre les modèles sans bris de symétrie"
                                "\npar nombre de semaines en " + str(timeout) + " secondes")
    plt.savefig("../plot/solution_loss_model.png")

    plot_solution_loss_by_symmetry(no_fail, timeout,
                                   "Comparaison du nombre de solutions en moyenne entre les modèles"
                                   "\nsans et avec bris de symétrie sous " + str(timeout) + " secondes")
    plt.savefig("../plot/solution_loss_symmetry.png")

    plot_time_by_model(no_fail, solver_no_fail, timeout,
                       "Comparaison du temps de résolution pour une solution entre les modèles"
                       "\nsans et avec bris de symétrie hors timeout")
    plt.savefig("../plot/time_by_model.png")

    plot_found_solution_by_model(no_fail, solver_no_fail, timeout,
                                 "Comparaison de combien de fois une solution est trouvée entre les modèles"
                                 "\nsans et avec bris de symétrie hors timeout")
    plt.savefig("../plot/found_solution_by_model.png")

    plt.show()


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) < 3:
        print("Usage: python src.graphs <path to log file>")
        exit(1)

    main(argv[1], argv[2])
