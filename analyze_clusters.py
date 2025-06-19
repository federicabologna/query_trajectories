import os
import json
from collections import defaultdict, Counter

def analyze_clustering_results(jsonl_path):
    total_users = 0
    users_with_clusters = 0

    total_clusters = 0
    total_queries_in_clusters = 0
    total_queries_all_users = 0
    cluster_counts = []
    avg_queries_per_cluster_all = []
    transition_type_counter = Counter()

    with open(jsonl_path, "r") as f:
        for line in f:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue  # skip malformed lines

            total_users += 1
            num_clusters = data.get("num_clusters", 0)
            clusters = data.get("clusters", [])
            transitions = data.get("common_transition_types", [])

            if clusters and num_clusters > 0:
                users_with_clusters += 1
                cluster_counts.append(num_clusters)
                total_clusters += num_clusters

                cluster_sizes = [len(cluster.get("queries", [])) for cluster in clusters]
                total_queries_in_clusters += sum(cluster_sizes)
                avg_queries_per_cluster_all.extend(cluster_sizes)

            # Count transition types
            if isinstance(transitions, list):
                for t in transitions:
                    t = t.strip().lower()
                    transition_type_counter[t] += 1

            # Estimate total user queries based on clustered queries
            total_queries_all_users += sum(len(cluster.get("queries", [])) for cluster in clusters)

    # Summary metrics
    avg_clusters_per_user = sum(cluster_counts) / len(cluster_counts) if cluster_counts else 0
    avg_queries_per_cluster = sum(avg_queries_per_cluster_all) / len(avg_queries_per_cluster_all) if avg_queries_per_cluster_all else 0
    query_coverage_ratio = total_queries_in_clusters / total_queries_all_users if total_queries_all_users else 0
    user_cluster_ratio = users_with_clusters / total_users if total_users else 0

    # Print core stats
    print(f"Total users: {total_users}")
    print(f"Users with clusters: {users_with_clusters}")
    print(f"Average number of clusters per user (with clusters): {avg_clusters_per_user:.2f}")
    print(f"Average number of queries per cluster: {avg_queries_per_cluster:.2f}")
    print(f"Proportion of queries in clusters: {query_coverage_ratio:.2%}")
    print(f"Proportion of users with clusters: {user_cluster_ratio:.2%}")
    print("\nMost Common Query Transition Types:")
    for ttype, count in transition_type_counter.most_common():
        print(f"- {ttype}: {count} occurrence(s)")


if __name__ == "__main__":
    analyze_clustering_results(os.path.join("output", "sqa_clustered.jsonl"))  # Replace with your file path
