import pandas as pd
import collections as co
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import imageio

def top_domain():
    df = pd.DataFrame(pd.read_csv("./Repository.csv"))
    df_clear = df.drop(df[df['topics'] == "[]"].index)

    words = []

    for index, row in df_clear.iterrows():
        topics = row.topics
        topics = topics.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
        split_topics = topics.split(',')
        words += split_topics

    topic_frequency = co.Counter(words)
    most_fq = topic_frequency.most_common()

    colormap = colors.ListedColormap(["gray", "green", "brown", "blue",  "red",  "black"])
    wc = WordCloud(scale=2, width=2000, height=2000, background_color="white", colormap=colormap, max_words=150).generate_from_frequencies(dict(most_fq))
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
    wc.to_file('wordcloud.pdf')

def trending_projects():
    data = {'rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'project': ['microsoft/vscode', 'MicrosoftDocs/azure-docs', 'flutter/flutter', 'firstcontributions/first-contributions',
                        'tensorflow/tensorflow', 'facebook/react-native', 'kubernetes/kubernetes', 'DefinitelyTyped/DefinitelyTyped',
                        'ansible/ansible', 'home-assistant/home-assistant'],
            'contributors': [19100, 14000, 13000, 11600, 9900, 9100, 6900, 6900, 6800, 6300]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(12, 10))
    plt.bar(df.project, df.contributors, 0.6)
    plt.xlabel("projects")
    plt.tick_params(axis='x', labelsize=7)
    plt.xticks(rotation=30)
    plt.ylabel("number of contributors")
    plt.title("top 10 trending projects")
    # plt.savefig("trending_project.pdf")
    plt.show()

def fastest_growing_projects():
    data = {'rank': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'project': ['aspnet/AspNetCore', 'flutter/flutter', 'MicrosoftDocs/vsts-docs',
                        'istio/istio', 'aws-amplify/amplify-js', 'helm/charts', 'ValveSoftware/Proton',
                        'gatsbyjs/gatsby',
                        'storybookjs/storybook', 'cypress-io/cypress'],
            'percentage': [346, 279, 264, 194, 188, 184, 182, 179, 178, 178]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(12, 10))
    plt.bar(df.project, df.percentage, 0.6)
    plt.xlabel("projects")
    plt.tick_params(axis='x', labelsize=7)
    plt.xticks(rotation=30)
    plt.ylabel("change in contributions(percentage)")
    plt.title("Fastest growing open source projects by contributors")
    plt.savefig("fastest_growing_project.pdf")
    plt.show()


top_domain()
# fastest_growing_projects()