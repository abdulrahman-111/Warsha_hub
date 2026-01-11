from sklearn.model_selection import train_test_split
import numpy as np
from typing import List, Tuple, Optional
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
from  matplotlib.colors import ListedColormap

#===============backend imports
from . import social_network
from . import db_manager
from . import USER

#============== engine import
from prediction_engine import  KNN



## 2 class dataset        #label (a,b) follow or not
network =social_network.get_social_network()
y=network ## matrix of labels



def prepare_data(size):
    X : []  # feature vector for all sample (i,j)
    y: []
    for i in range(size):
        for j in range(size):
            if(i == j ): continue

            user1=db_manager.return_user_by_id(i)
            user2=db_manager.return_user_by_id(j)

            if not user1 or not user2:
                continue

            my_interests_1 = set(user1.get_interests())
            my_interests_2 = set(user2.get_interests())

            jaccard=network._jaccard_similarity(i,j)
            cos=network._cosine_similarity(my_interests_1,my_interests_2)
            mutual= db_manager.get_mutual_friends_count(i,j)
            X.append([jaccard,cos,mutual])
            y.append(network[i,j])

    return np.array(X), np.array(y)


# ------------------- Prepare dataset
size=network.return_num_of_users()
X, y = prepare_data(size)


X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)



clf =KNN(k=3)
clf.fit(X_train,y_train)

predictions = clf.predict(X_test)

acc =np.sum( predictions==y_test) / len(y_test)
print(acc)

# ------------------- Train KNN use built-in funcitons
knn = KNeighborsClassifier(n_neighbors=5, metric="euclidean")
knn.fit(X_train, y_train)

# ------------------- Evaluation
accuracy = knn.score(X_test, y_test)
print(f"✅ KNN of built in model Accuracy: {accuracy:.4f}")

def predict_follow(user1_id:int , user2_id, int):
    user1 = db_manager.return_user_by_id(user1_id)
    user2 = db_manager.return_user_by_id(user2_id)

    my_interests_1_temp = set(user1.get_interests())
    my_interests_2_temp = set(user2.get_interests())

    jaccard_temp = network._jaccard_similarity(user1_id, user2_id)
    cos_temp = network._cosine_similarity(my_interests_1_temp, my_interests_2_temp)
    mutual_temp = db_manager.get_mutual_friends_count(user1_id, user2_id)
    x_follow=[jaccard_temp,cos_temp,mutual_temp]
    engine=KNN(k=3)

    return engine.predict_one(x_follow)




cmap = ListedColormap(['#FF0000','#00FF00','#0000FF'])

plt.figure()
plt.scatter(X[:,0],X[:,1] , c=y,cmap=cmap,edgecolors='k',s=20)
plt.show()