import re  # 用于从结果中提取分数
from datetime import datetime
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Score, RegistrationKey, Info
from translate_project.settings import KIMI_API_KEY
from openai import OpenAI


# 配置 KimiAPI 的 OpenAI 客户端
client = OpenAI(
    api_key=KIMI_API_KEY,  # 请替换为你从 Kimi 开放平台申请的 API Key
    base_url="https://api.moonshot.cn/v1",
)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # 获取密钥
            registration_key = form.cleaned_data['registration_key']
            try:
                key = RegistrationKey.objects.get(key=registration_key, is_used=False)
            except RegistrationKey.DoesNotExist:
                messages.error(request, "无效或已使用的注册密钥！")
                return render(request, 'translate_app/register.html', {'form': form})

            # 创建用户
            user = form.save()

            # 创建用户信息并绑定密钥
            Info.objects.create(user=user, registration_key=key)

            # 标记密钥为已使用
            key.is_used = True
            key.save()

            messages.success(request, "注册成功！请登录。")
            return redirect('login')
        else:
            messages.error(request, "注册信息有误，请检查后重试！")
    else:
        form = CustomUserCreationForm()

    return render(request, 'translate_app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('translate_view')  # 或者其他你想跳转的页面
    else:
        form = CustomAuthenticationForm()
    return render(request, 'translate_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "您已成功退出登录！")
    return redirect('login')


def score_translation(original_text, translated_text):
    try:
        # 通过 OpenAI 客户端调用 KimiAPI
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，专门用于英语到中文翻译的质量评价和反馈。你的任务是根据用户提供的英文原文和中文译文(文章来源于考研英语)，提供翻译的评分（请以'评分：X分'格式给出，满分为15分）和详细的评价，包括译文的准确性、流畅性以及是否符合原文含义。请确保你的反馈清晰、客观，能帮助用户提升翻译质量。"},
                {"role": "user", "content": f"英文原文：{original_text}，中文译文：{translated_text}"}
            ],
            temperature=0.3,
        )
        
        # 提取评分和评价信息
        assistant_reply = completion.choices[0].message.content
        return assistant_reply

    except Exception as e:
        return f"错误: {str(e)}"


@login_required(login_url='login')
def translate_view(request):
    current_year = datetime.now().year
    range_now_to_past = list(range(current_year, current_year - 20, -1))

    if request.method == 'POST':
        original_text = request.POST.get('original_text')
        translated_text = request.POST.get('translated_text')
        year = request.POST.get('year')

        # 调用 KimiAPI 以获取评分和评价
        result = score_translation(original_text, translated_text)

        # 使用正则表达式提取评分
        match = re.search(r"评分[:：]\s*(\d+(?:\.\d+)?)", result)
        if match:  # 确保匹配成功
            score = float(match.group(1))  # 提取评分数字
            review = result  # 评价内容

            # 保存到数据库
            Score.objects.create(
                user=request.user,
                original_text=original_text,
                translated_text=translated_text,
                score=score,
                review=review,
                year=year
            )

            return render(request, 'translate_app/translate_result.html', {
                'original_text': original_text,
                'translated_text': translated_text,
                'result': review,
                'score': score
            })
        else:
            # 如果匹配不到评分，返回错误页面或显示错误消息
            return render(request, 'translate_app/translate_form.html', {
                'error': '无法从结果中提取评分，请检查输入或稍后再试。',
                'range_now_to_past': list(range(datetime.now().year, datetime.now().year - 20, -1))
            })

    # 查询所有历史记录并按上传时间倒序排列
    history_records = Score.objects.filter(user=request.user).order_by('-upload_time')
    paginator = Paginator(history_records, 5)  # 每页5条数据

    # 获取当前页码（默认为1）
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 将分页对象传递到模板
    return render(request, 'translate_app/translate_form.html', {
        'range_now_to_past': range_now_to_past,
        'page_obj': page_obj  # 新增的分页对象
    })
