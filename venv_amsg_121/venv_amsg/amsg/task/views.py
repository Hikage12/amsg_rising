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
        # randlst = [random.choice(string.ascii_letters + string.digits)
        #            for i in range(10)]
        # random_string = ''.join(randlst)
        # print("************************")
        # print(random_string)
        # print("************************")
        obj.set_password(obj.password)

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

    def task_info(request, pk):
        if request.method == 'POST':
            if 'task-del' in request.POST:
                delete_record = Task.objects.filter(id=pk)
                delete_record.delete()
            return redirect('task:task_list')


class TaskInfo2View(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = 'task_info.html'

    def task_edit(request, pk):
        if request.method == 'POST':
            if 'task-taskdel' in request.POST:
                delete_record = Question.objects.filter(id=pk)
                print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                delete_record.delete()
                print("dddddddddddddddddddddddddddddddddddddddddddddddddddd")
            return redirect('task:task_edit')


class TaskEditView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    template_name = 'task_edit.html'
    form_class = TaskCreateForm

    # def get_context_data(self,*args,**kwargs):
    #    context = super().get_context_data(*args,**kwargs)
    #    context['quest_list'] = Question.objects.filter(
    #        q_task=Task.objects.get(id=self.kwargs['pk'])
    #        )
    #    return context
    def get_success_url(self):
        return reverse_lazy('task:task_info', kwargs={'pk': self.kwargs['pk']})


class QuestionAddView(LoginRequiredMixin, generic.CreateView):
    model = Question
    template_name = "quest_add.html"
    form_class = QuestionCreateForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        # 作成時に紐づける
        obj.q_task = Task.objects.get(id=self.kwargs['pk'])
        obj.q_school = self.request.user.user_school

        obj.save()
        messages.success(self.request, 'クラスを作成しました。')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task:task_info', kwargs={'pk': self.kwargs['pk']})


class QuestionEditView(LoginRequiredMixin, generic.UpdateView):
    model = Question
    template_name = 'quest_edit.html'
    form_class = QuestionCreateForm

    def get_success_url(self):
        q_data = Question.objects.get(id=self.kwargs['pk'])
        return reverse_lazy('task:task_info', kwargs={'pk': q_data.q_task.id})


class QuestiondeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Question
    template_name = 'question_delete.html'
    success_url = reverse_lazy('task:task_list')

    def delete(self, request, *args, **kwargs):
        # 教科書意味なし
        # delete
        return super().delete(request, *args, **kwargs)
        # superで子クラスから親クラスの変数とメソッドを参照し持ってくることでdeleteさせる。


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

    # postされたらすぐ採点させようかな
    # Questionのレコードを表示順に取得したい
    # -> q_task = task_dataの問題レコードをリストで取得
    def post(self, request, *args, **kwargs):
        task_data = Task.objects.get(id=self.kwargs['pk'])
        """
        post されてきた解答をリストで格納
        出題されている問題オブジェクトをリストで格納
        index が同じ要素をそれぞれ比較して点数つけてく
        計算した点数を諸々紐づけて成績レコードを生成する
        """
        # postされてきた解答のリスト
        ans_list = request.POST.getlist('answer')
        # 出題されている問題オブジェクトのリスト
        # quest_data_list --> queryset型でlistに格納
        # for data in quest_data_list: で個別のQuestionオブジェクト取得できる
        # data.q_statement -> その問題レコードの問題文取得できる
        quest_data_list = Question.objects.filter(q_task=task_data)
        sum = 0
        print("**********************")
        for index in range(len(ans_list)):
            if quest_data_list[index].q_answer == ans_list[index]:
                sum += quest_data_list[index].q_point

            print(quest_data_list[index].q_statement)
            print(ans_list[index])
        ExamHistory.objects.create(
            exam_user=self.request.user,
            exam_task=task_data,
            exam_score=sum
        )
        print("合計点:", sum)
        print("**********************")

        return redirect('task:toppage')


class ExamTakeListView(LoginRequiredMixin, generic.ListView):
    model = ExamHistory
    template_name = "exam_history.html"

    def get_queryset(self):
        return ExamHistory.objects.filter(
            exam_user=self.request.user
        )


class PersonalScoreView(LoginRequiredMixin, generic.DetailView):
    model = ExamHistory
    template_name = "personal_score.html"


class ExamTaskListView(LoginRequiredMixin, generic.ListView):
    model = Distribution
    template_name = "exam_task_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['dist_list'] = Distribution.objects.all()
        return context


class ExamClassListView(LoginRequiredMixin, generic.ListView):
    model = Class
    template_name = "exam_class_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        task_data = Task.objects.get(id=self.kwargs['pk'])
        context['dist_data_list'] = Distribution.objects.filter(
            distribute_task=task_data
        )
        return context


class ExamStudentListView(LoginRequiredMixin, generic.ListView):
    model = CustomUser
    template_name = "exam_stu_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        class_data = Class.objects.get(id=self.kwargs['pk'])
        context['stu_list'] = CustomUser.objects.filter(
            user_class=class_data,
            user_auth='3'
        )
        return context


class StudentScoreView(LoginRequiredMixin, generic.TemplateView):
    template_name = "student_score.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        stu_data = CustomUser.objects.get(id=self.kwargs['pk'])
        context['exam_list'] = ExamHistory.objects.filter(
            exam_user=stu_data
        )
        return context
