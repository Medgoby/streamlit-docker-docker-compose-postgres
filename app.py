# local
import content

# 3rd party
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
#from dtreeviz.trees import *
#from dtreeviz.trees import dtreeviz

#from sklearn.datasets import load_boston
#from sklearn.datasets import load_boston

from sklearn.tree import DecisionTreeRegressor
import psycopg2
from dotenv import find_dotenv, load_dotenv

# built-in
import os
import base64

@st.cache()
def load_data():
    boston = pd.read_csv('./boston.csv')
    X = boston.loc[:,~boston.columns.isin(['PRICE'])]
    y=boston['PRICE'].to_frame()
    feature_names = boston.columns
    return X, y, feature_names

@st.cache()
def fit_dtree(X, y):
    """
    With bigger data, or a more complex model,
    you'd probably want to train offline, then
    load into app.
    """
    dtree = DecisionTreeRegressor(max_depth=2)
    dtree.fit(X, y)
    return dtree

def render_svg(svg):
    """
    Renders the given svg string.
    https://gist.github.com/treuille/8b9cbfec270f7cda44c5fc398361b3b1
    """
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def get_dt_graph(dt_classifier):
    fig = plt.figure(figsize=(25,20))
    _ = tree.plot_tree(dt_classifier,
                       feature_names=X.columns,
                       filled=True)

if __name__ == "__main__":
    ### loading things up
    text = st.sidebar.title("Built on:")
    logo = st.sidebar.image("images/streamlit.png")
    logo = st.sidebar.image("images/docker.png")
    logo = st.sidebar.image("images/aws.png")
    logo = st.sidebar.image("images/postgres.png")

    # text content
    title = st.title("Explainable ML")
    intro = st.markdown(content.intro)
    model_explanation = st.markdown(content.model_explanation)
    slider_explanation = st.markdown(content.slider_explanation)

    # fitting model
    X, y, feature_names = load_data()
    dtree = fit_dtree(X, y)

    # sliders for new predictions
    RM = st.slider("RM: average number of rooms per dwelling.",
                         min_value=3.6,
                         max_value=8.7,
                         value=6.0,
                         step=.1)
    LSTAT = st.slider("LSTAT: percentage of the population denoted as lower status.",
                         min_value=2.0,
                         max_value=37.0,
                         value=14.0,
                         step=.1)
    new_observation = np.array([0, 0, 0, 0, 0, RM, 0, 0, 0, 0, 0, 0, LSTAT])

    viz = get_dt_graph(dtree)
    # viz the predictions path
    #viz = dtreeviz(dtree,
    #           X,
    #           y,
    #           target_name='price',
    #           orientation ='LR',  # left-right orientation
    #           feature_names=feature_names,
    #           X=new_observation)  # need to give single observation for prediction
    #viz.save("images/prediction_path.svg")

    # read in svg prediction path and display
    with open("images/prediction_path.svg", "r") as f:
        svg = f.read()
    render_svg(svg)
    prediction_explanation = st.markdown(f"""According to the model, a house with {round(RM, 1)} rooms located in a neighborhood that is {LSTAT/100:.1%} lower status
should be valued at approximately ${dtree.predict(new_observation.reshape(1, -1)).item():,.0f}.""")

    st.title("Connecting with `postgres`")
    st.markdown(content.postgres_explanation)

    condition = ""
    if RM  < 6.94:
        condition +=  "rm < 6.94"
        if LSTAT  < 14.40:
            condition += " and lstat < 14.40"
        else:
            condition += " and lstat >= 14.40"
    else:
        condition += "rm >= 6.94"
        if RM < 7.437:
            condition += " and rm < 7.437"
        else:
            condition += " and rm >= 7.437"


    query = f"""select *
from boston
where {condition}
"""
    st.markdown(f"""
```
{query}
```
""")

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(load_dotenv())
    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")

    conn = psycopg2.connect(host='postgres',
                       port='5432',
                       dbname=dbname,
                       user=user,
                       password=password
                        )

    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()

    # getting col names for display df
    cur.execute("select * from boston limit 0;")
    col_names = [desc[0].upper() for desc in cur.description]
    cur.close()
    conn.close()

    # displaying df
    df = pd.DataFrame(result, columns=col_names)
    st.dataframe(df)