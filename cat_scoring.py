import streamlit as st
from PIL import Image, ImageDraw
import torch
import torchvision.transforms as T
import timm

@st.cache_resource
def load_model():
    model = timm.create_model("resnet34", pretrained=True)
    model.eval()
    return model

def get_score(model, image):
    transforms = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor()
    ])

    image = transforms(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(image)
        probs = torch.nn.functional.softmax(outputs, dim=1)[0]

    cat_indices = [281, 282, 283, 294, 295]
    cat_labels = {
        281: "tabby cat",
        282: "tiger cat",
        283: "Persian cat",
        284: "Siamese cat",
        285: "Egyptian cat"
    }

    max_score = 0
    total_score = 0

    for idx in cat_indices:
        if max_score < probs[idx].item()*100:
            max_score = probs[idx].item() * 100
            max_label = cat_labels[idx]
        total_score += probs[idx].item()*100

    return max_score, max_label, total_score

def cat_scoring():
    st.sidebar.image("cat_scoring_example.png")
    model = load_model()
    model.to('cpu')

    st.title("🐱 고양이를 그려라!")

    # 이미지 업로드
    uploaded_file = st.file_uploader("고양이가 포함된 이미지를 업로드하세요.", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # 이미지 열기 및 변환
        image = Image.open(uploaded_file).convert('RGB')

        # 점수
        max_score, max_label, total_score = get_score(model, image)

        draw = ImageDraw.Draw(image)

        # 결과 출력
        st.image(image, caption="고양이 탐지 결과", use_column_width=True)


        st.markdown(f"## 📊 고양이 그림 점수")
        st.markdown(f"### 점수 : {total_score*100:.2f}")
        st.markdown(f"### 최고 점수 ({max_label}) : {max_score*100:.2f}")
        if total_score*100 < 60:
            st.warning("고양이가 없네요? 다시 그려보세요!")
