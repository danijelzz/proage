from graph import graph


def main():

    print("\n=== Navigator Zdravstvenog Sustava ===\n")

    user_input = input(
        "Unesite nalaz, simptome ili lijekove:\n\n"
    )

    result = graph.invoke({
        "user_input": user_input
    })

    print("\n")
    print("=" * 50)
    print("ZAVRŠNI SAŽETAK")
    print("=" * 50)
    print("\n")

    print(result["final_summary"])

    print("\n")
    print("=" * 50)
    print("DETALJNI DIJAGNOSTIČKI IZVJEŠTAJ")
    print("=" * 50)
    print("\n")

    print(result["diagnostic_report"])

    print("\n")
    print("=" * 50)
    print("FARMACEUTSKI IZVJEŠTAJ")
    print("=" * 50)
    print("\n")

    print(result["medication_report"])


if __name__ == "__main__":
    main()