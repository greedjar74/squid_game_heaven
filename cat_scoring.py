import streamlit as st
from PIL import Image, ImageDraw
import torch
import torchvision.transforms as T

def get_score(model, image):
    transforms = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor()
    ])

    image = transforms(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(image)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        
    return probs.cpu().numpy()[0][0] * 100


def cat_scoring():
    # 저장된 모델 로드
    model = torch.load("best_model.pth")
    model.to('cpu')

    st.title("🐱 고양이를 그려라!")

    # 이미지 업로드
    uploaded_file = st.file_uploader("고양이가 포함된 이미지를 업로드하세요.", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # 이미지 열기 및 변환
        image = Image.open(uploaded_file).convert('RGB')

        # 점수
        score = get_score(model, image)

        draw = ImageDraw.Draw(image)

        # 결과 출력
        st.image(image, caption="고양이 탐지 결과", use_column_width=True)


        st.markdown(f"### 📊 고양이 그림 점수: {score:.2f}")

        if score < 60:
            st.warning("고양이가 없네요? 다시 그려보세요!")
