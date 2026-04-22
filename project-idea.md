Ideas

- Analysis on gen Z/gen Alpha slangs  
- Come up with “eigenslang” (eigen vector of slangs)  
- Predict or generate new slang from existing words  
- Possibly help AI models understand slangs (like slang \- eigenslang \= neutral/original word)  
- Slang translation

Rationale:

Literature Review:  
The topic of slangs and dealing with slangs is a significant topic/challenge for NLP and LLMs

- Urban Dictionary Embeddings for Slang NLP Applications (Wilson et. al.)  
- [https://medium.com/data-science/visualization-of-word-embedding-vectors-using-gensim-and-pca-8f592a5d3354](https://medium.com/data-science/visualization-of-word-embedding-vectors-using-gensim-and-pca-8f592a5d3354)  
- Analyzing Semantic Properties of Word Embeddings Using Eigenvectors (Abdlrazg & Atetalla)  
- Cringe, lit, or mid: affective and cognitive effects of youth slang in an educational chatbot  
  - This one is for why it’s good to have youth slangs in chatbots  
- The Evolution of Gen Alpha Slang: Linguistic Patterns and AI Translation Challenges  
  - Looks at Gen “Alpha” slang and how analysis could provide insight for AI translation of these slangs  
- Slang feature extraction by analysing topic change on social media  
  - [https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/trit.2018.1060](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/trit.2018.1060)  
- A Computational Framework for Slang Generation  
  - “Generative process” for slangs  
  - Bert is not good 


Hypothesis:

Methodology:

Contribution to Present Research:

The three main questions your project proposal needs to answer are:  
1\. What problem you are focusing on?  
Attempting to better understand Gen Z slang, the relationships between them and contribute to the field of linguistics through our analysis (perhaps guide the prediction of new slang)

2\. What do you plan to do?

1. Scrap web data on slangs and their context/examples and their neutral words (twitter, reddit, instagram)  
   1. And parse for vector embedding use  
2. Retrain / tune a pre-existing word to vector embedding model or perhaps:  
   1. Use pre-trained models like **fastText** (which handles "out-of-vocabulary" slang by looking at subwords) or **BERT** to get high-dimensional vectors for both slang and neutral words  
3. Find the difference vectors between each slang and their associated “neutral/non-slang” word   
4. Apply PCA or SVD to the difference vectors to reduce the dimentionalities  
   1. Hypothesize that the first eigenvector or “eigenslang” represents the slangness   
5. Analysis/visualization of the eigenslang  
   1. Visualize slangs vs non slangs (clustering)  
   2. Observe “new” slangs by applying the eigenslang to different neutral words  
   3. Apply slang \- eigenslang to get the original word or synonyms of the original word  
6. Discuss our findings, possible improvements/failures and future research/applications

3\. What will the “contribution” be?

- Slang translation app/feature to bridge the gap in online communication (widening gap between generations)  
  - Helps millennials keep up to date  
- Assist AI models in understanding slangs and their use/context  
  - Younger generations tend to be the primary users of AI chatbots