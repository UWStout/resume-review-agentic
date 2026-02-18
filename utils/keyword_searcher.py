from itertools import compress

# Count the occurrences of each of the given keywords within the given Documents
def count_keywords(docs, keywords):
    # List of counts for each keyword
    counts = [0] * len(keywords)

    # Loop over all "docs"
    for content_doc in docs:
        # Call 'count' for each keyword
        doc_counts = [content_doc.page_content.count(keyword) for keyword in keywords]

        # Accumulate the keyword counts in the counts list
        counts = [counts[i] + new_count for i, new_count in enumerate(doc_counts)]

    # Return the list of keyword counts
    return counts

# Analyze and provide feedback on the keyword counts given
def analyze_keyword_counts(counts, keywords, type_name, description):
    # Output a header for this analysis
    output = f"## {type_name.title()} Keywords\n"

    # Create a true/false mask for any keywords with a count of zero (or less)
    zero_count_mask = list(map(lambda x: x < 1, counts))
    if any(zero_count_mask):
        # List out the missing keywords
        output += f"The following keywords describing {description} may be missing:\n"

        # Use the mask to build a list of missing keywords and iterate over it
        for missing in list(compress(keywords, zero_count_mask)):
            output += f"- {missing}\n"
        output += "\nConsider adding these to your resume.\n"
    else:
        # Output a message that all are present
        output += f"It looks like you've included all the recommended {type_name.lower()} keywords.\n"

    # Return the analysis
    return output
