from base64 import encode
from operator import truediv
from tabnanny import verbose
from django.db import models
from accounts.models import *
from django_currentuser.db.models import CurrentUserField
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user
)

# Create your models here.


class Task(models.Model):
    SELECTION = (
        ('0', '非公開'),
        ('1', '公開'),
    )

    task_school = models.ForeignKey(
        School, verbose_name='学校', default=0, on_delete=models.PROTECT)
    task_name = models.CharField(verbose_name='課題名', max_length=20)
    task_subject = models.CharField(
        verbose_name='教科', null=True, max_length=20)
    task_smallsubject = models.CharField(
        verbose_name='科目', null=True, max_length=20)
    task_score = models.IntegerField(verbose_name='総得点', default=100)
    task_time = models.IntegerField(verbose_name='課題時間', default=60)
    task_status = models.CharField(
        verbose_name='状態', choices=SELECTION, default='0', max_length=1)
    task_create_date = models.DateTimeField(
        verbose_name='作成日時', auto_now_add=True)
    task_update_date = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    task_created_by = CurrentUserField(
        verbose_name='作成者', related_name='task_created_by')

    def save(self, *args, **kwargs):
        self.task_created_by = get_current_authenticated_user()
        super(Task, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Task'

    def __str__(self):
        return self.task_name


class Question(models.Model):
    SELECTION = (
        ('0', '非公開'),
        ('1', '公開'),
    )
    SELECTION1 = (
        ('0', 'off'),
        ('1', 'on'),
    )

    q_school = models.ForeignKey(
        School, verbose_name='学校', on_delete=models.PROTECT)
    q_task = models.ForeignKey(
        Task, verbose_name='課題', on_delete=models.CASCADE)
    q_statement = models.TextField(verbose_name='問題文', blank=True, null=True)
    q_answer = models.CharField(verbose_name='解答', max_length=200)
    q_point = models.IntegerField(verbose_name='配点', null=True)
    q_autostatus = models.CharField(
        verbose_name='自動採点', choices=SELECTION1, default='1', max_length=1)
    q_created_by = CurrentUserField(
        verbose_name='作成者', related_name='q_created_by')
    q_create_date = models.DateTimeField(
        verbose_name='作成日時', auto_now_add=True)
    q_update_date = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Question'


class Distribution(models.Model):
    distribute_task = models.ForeignKey(
        Task, verbose_name='課題', on_delete=models.CASCADE)
    distribute_class = models.ForeignKey(
        Class, verbose_name='クラス', on_delete=models.CASCADE)
    distribute_date = models.DateTimeField(
        verbose_name='配布日時', auto_now=True, null=True)

    class Meta:
        verbose_name_plural = 'Distribution'

    def __str__(self):
        return self.distribute_task.task_name


# 追加
class Answer(models.Model):
    ans_task = models.ForeignKey(
        Task, verbose_name='課題', on_delete=models.CASCADE)
    ans_quest = models.ForeignKey(
        Question, verbose_name='問題', on_delete=models.CASCADE)
    ans_user = models.ForeignKey(
        CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    ans_q_statement = models.TextField(
        verbose_name='問題文', blank=True, null=True)
    ans_q_ans = models.CharField(verbose_name='模範解答', max_length=200)
    ans_data = models.CharField(verbose_name='解答', max_length=200)

    class Meta:
        verbose_name_plural = 'Answer'


class ExamHistory(models.Model):
    exam_user = models.ForeignKey(
        CustomUser, verbose_name='受験ユーザー', null=True, on_delete=models.SET_NULL)
    exam_task = models.ForeignKey(
        Task, verbose_name='課題', on_delete=models.CASCADE)
    exam_score = models.IntegerField(verbose_name='成績')
    exam_date = models.DateTimeField(verbose_name='受験日', auto_now=True)

    class Meta:
        verbose_name_plural = 'ExamHistory'
