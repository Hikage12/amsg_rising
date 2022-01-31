from email import message
from urllib.parse import quote_from_bytes
from django.shortcuts import render
from django.views import generic
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from accounts.models import *
from task.models import *
from .forms import *
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

import random
import string
import re

# Create your views here.


class ToppageView(LoginRequiredMixin, generic.TemplateView):
    template_name = "toppage.html"


class UserListView(LoginRequiredMixin, generic.ListView):
    model = CustomUser
    template_name = "user_list.html"

    def get_queryset(self):
        return CustomUser.objects.all()


# ユーザー登録view
class UserCreateView(LoginRequiredMixin, generic.CreateView):
    model = CustomUser
    template_name = "user_create.html"
    form_class = UserCreateForm
    success_url = reverse_lazy('task:user_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        # 作成時に紐づける
        obj.user_school = self.request.user.user_school

        # ランダム文字列生成
        randlst = [random.choice(string.ascii_letters + string.digits)
                   for i in range(10)]
        random_string = ''.join(randlst)
        print("************************")
        print(random_string)
        print("************************")
        obj.set_password(random_string)

        obj.save()
        messages.success(self.request, 'ユーザーを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '失敗しました。')
        return super().form_invalid(form)


class UserInfoView(LoginRequiredMixin, generic.DetailView):
    model = CustomUser
    template_name = 'user_info.html'

    def user_info(request, pk):
        if request.method == 'POST':
            if 'user-del' in request.POST:
                delete_record = CustomUser.objects.filter(id=pk)
                delete_record.delete()
            return redirect('task:user_list')


class UserEditView(LoginRequiredMixin, generic.UpdateView):
    model = CustomUser
    template_name = 'user_edit.html'
    form_class = UserEditForm

    def get_success_url(self):
        return reverse_lazy('task:user_info', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, 'ユーザーの名前を変更しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '編集に失敗しました')
        return super().form_invalid(form)


class ClassListView(LoginRequiredMixin, generic.ListView):
    model = Class
    template_name = 'class_list.html'

    def get_queryset(self):
        return Class.objects.all()


class ClassCreateView(LoginRequiredMixin, generic.CreateView):
    model = Class
    template_name = "class_create.html"
    form_class = ClassCreateForm
    success_url = reverse_lazy('task:class_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        # 作成時に紐づける
        obj.class_school = self.request.user.user_school

        obj.save()
        messages.success(self.request, 'クラスを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '失敗しました。')
        return super().form_invalid(form)


class ClassInfoView(LoginRequiredMixin, generic.DetailView):
    model = Class
    template_name = "class_info.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['stu_list'] = CustomUser.objects.filter(
            user_school=self.request.user.user_school,
            user_class=Class.objects.get(id=self.kwargs['pk'])
        )
        return context

    def class_info(request, pk):
        if request.method == 'POST':
            if 'class-del' in request.POST:
                delete_record = Class.objects.filter(id=pk)
                delete_record.delete()
            return redirect('task:class_list')


class ClassEditView(LoginRequiredMixin, generic.UpdateView):
    model = Class
    template_name = 'class_edit.html'
    form_class = ClassCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['stu_list'] = CustomUser.objects.filter(
            user_school=self.request.user.user_school,
            user_auth='3'
        )
        return context

    def post(self, request, *args, **kwargs):
        # postで送られてきた生徒データがlist状でpk_listに格納される
        pk_list = request.POST.getlist('add')
        # classinfoで使ったpkのクラスのインスタンスが欲しい -> get
        # self.kwargs['pk'] = 2
        class_data = Class.objects.get(
            id=self.kwargs['pk'])  # 現在編集してるClassインスタンスのidを取得

        # 送られてきたstudentのidを一つずつ取り出し、それを使ってStudentインスタンス取得
        # studentインスタンスのuser_class情報に現在編集してるクラスのインスタンスを指定する
        # studentインスタンスを保存
        for stu_pk in pk_list:
            student = CustomUser.objects.get(id=stu_pk)
            student.user_class = class_data
            student.save()

        return redirect("task:class_info", pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('task:class_info', kwargs={'pk': self.kwargs['pk']})


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "task_list.html"

    def get_queryset(self):
        tasks = Task.objects.filter(task_school=self.request.user.user_school)
        return tasks


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    template_name = "task_create.html"
    form_class = TaskCreateForm
    success_url = reverse_lazy('task:task_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        # 作成時に紐づける
        obj.task_school = self.request.user.user_school
        obj.save()
        messages.success(self.request, 'ユーザーを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '失敗しました。')
        return super().form_invalid(form)


class TaskInfoView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = 'task_info.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['quest_list'] = Question.objects.filter(
            q_task=Task.objects.get(id=self.kwargs['pk'])
        )
        return context


class TaskEditView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = 'task_edit.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['quest_list'] = Question.objects.filter(
            q_task=Task.objects.get(id=self.kwargs['pk'])
        )
        return context

    def post(self, request, *args, **kwargs):
        question_list = []
        answer_list = []
        score_list = []
        select_list = []
        print("*************")
        # 編集してるTaskオブジェクト取得
        task_data = Task.objects.get(id=self.kwargs['pk'])
        for i in request.POST.items():
            # ValueError:invalid literal for int() with base 10: ''
            # task_dataにint変換できないもの入れようとしてる？
            if re.match(r'task', i[0]):
                task_data.task_name = i[1]
                task_data.save()
            elif re.match(r'subject', i[0]):
                task_data.task_subject = i[1]
                task_data.save()
            elif re.match(r'smallsubject', i[0]):
                task_data.task_smallsubject = i[1]
                task_data.save()
            elif re.match(r'total', i[0]):
                # 点数入力欄に何も入力しないと空文字列が送られてvalueerror吐かれる
                task_data.score = i[1]
                task_data.save()

            elif re.match(r'question_*', i[0]):
                question_list.append(i[1])
            elif re.match(r'answer_*', i[0]):
                answer_list.append(i[1])
            elif re.match(r'score_*', i[0]):
                score_list.append(i[1])
            elif re.match(r'select_*', i[0]):
                select_list.append(i[1])

        for index in range(len(question_list)):
            question_statement = question_list[index]
            answer = answer_list[index]
            score = score_list[index]
            if select_list[index] == 'on':
                is_auto = '1'
            else:
                is_auto = '0'
            Question.objects.create(
                q_school=self.request.user.user_school,
                q_task=task_data,
                q_statement=question_statement,
                q_answer=answer,
                q_point=score,
                q_autostatus=is_auto
            )

        for j in question_list:
            print("statement:", end=' ')
            print(j)
        for k in answer_list:
            print("answer:", end=' ')
            print(k)
        for l in score_list:
            print("point:", end=' ')
            print(l)
        for m in select_list:
            print("select:", end=' ')
            print(m)
        print("*************")

        # post後の遷移処理
        return redirect("task:task_info", pk=self.kwargs['pk'])


class TaskSetView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    template_name = 'task_set.html'
    form_class = TaskSetForm

    # task_set.htmlで配布先クラスを表示できるように get_context_data 使う
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['class_list'] = Class.objects.filter(
            class_school=self.request.user.user_school
        )
        return context

    # 選択されたクラスに配布する
    def post(self, request, *args, **kwargs):
        # postで送られてきたclass_idをlist状でpk_listに格納
        pk_list = request.POST.getlist('distribute')
        task_data = Task.objects.get(
            id=self.kwargs['pk'])  # 現在編集してるTaskインスタンスのidを取得

        # Distribution.objects.create(task_obj,class_obj)
        # 配布する課題とクラスを Distributionクラスと紐づける
        for class_pk in pk_list:
            class_data = Class.objects.get(id=class_pk)
            # create()だけでDistributionオブジェクトを作成して保存できる
            distribution = Distribution.objects.create(
                distribute_task=task_data, distribute_class=class_data)
            print("********************")
            print(distribution.distribute_task)
            print(distribution.distribute_class)
            print("********************")
            # 課題クラスのstatusを公開にする
            task_data.task_status = '1'
            task_data.save()

        return redirect("task:task_info", pk=self.kwargs['pk'])


class PossibleTaskListView(LoginRequiredMixin, generic.ListView):
    model = Distribution
    template_name = 'possible_task_list.html'

    # 自分のクラスが Distributionクラスで紐づけられている Taskを見たい
    # 自分のクラス情報 -> class_data = user.user_class
    # Distributionクラスで紐づいてるTaskのクエリ情報
    #   -> Distribution.objects.filter(distribute_class=class_data)
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        class_data = self.request.user.user_class
        context['possible_task_list'] = Distribution.objects.filter(
            distribute_class=class_data
        )
        return context


class TakeExamView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = 'take_exam.html'


class AnswerView(LoginRequiredMixin, generic.ListView):
    model = Question
    template_name = 'answer.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        task_data = Task.objects.get(id=self.kwargs['pk'])
        context['q_list'] = Question.objects.filter(
            q_task=task_data
        )
        return context

    def post(self, request, *args, **kwargs):
        return redirect('task:toppage')
