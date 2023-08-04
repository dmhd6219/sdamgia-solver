from bs4 import BeautifulSoup
import colorama
from colorama import Fore
import requests


class Task:

    def __init__(self, text, images=None, answer="", task_id=0):
        self.text = text
        self.images = set()
        self.answer = answer
        self.task_id = task_id
        self.solutionLink = False

    def __eq__(self, other):
        return (self.text, self.images, self.answer, self.task_id) == (
            other.text, other.images, other.answer, other.task_id)

    def __str__(self):
        return "id: {}, {}".format(self.task_id, self.text)


class Solver:
    def __init__(self, variant_link, cookies):
        self.url_variant = variant_link
        self.url_domain = variant_link[:variant_link.index("/", 10) + 1]
        self.url_search = self.url_domain + "search?search={}&cb=1&body=3&text=2&page="
        self.url_task = self.url_domain + "problem?id="

        self.cookies = cookies

    def get_tasks(self, url):
        response = requests.get(url, cookies=self.cookies)
        soup = BeautifulSoup(response.text, "lxml")

        tasks = []
        for taskHTML in soup.findAll("div", class_="prob_maindiv"):
            task = None

            for p in taskHTML.findAll("p"):
                if p.text and p.text.strip() and not p.text.strip()[0].isdigit():
                    task = Task(p.text)
                    break

            for img in taskHTML.findAll("img"):
                src = img["src"]
                if not src.startswith("http"):
                    src = self.url_domain[:-1] + src
                task.images.add(src)

            answers = taskHTML.findAll("div", class_="answer")
            if answers:
                task.answer = answers[-1].text.rstrip(".").replace("|", "; Ответ: ").replace("&", " ")

            link = taskHTML.find("a", href=True)
            if link:
                task.task_id = link.text

            same_text = taskHTML.find("div", class_="probtext")
            if same_text and same_text.has_attr("id"):
                task.task_id = same_text["id"][4:]

            if "Впишите ответ на задание в поле выше или загрузите его" in taskHTML.parent.parent.text or \
                    "Решения заданий с развернутым ответом" in taskHTML.parent.parent.text:
                task.solutionLink = True
            # task.solutionLink = True
            tasks.append(task)
        return tasks

    def get_answer(self, task):
        if not task.answer and task.task_id:
            if task.solutionLink:
                task.answer = "Решение: " + self.url_task + str(task.task_id)
            else:
                task.answer = self.get_tasks(self.url_task + task.task_id)[0].answer
        else:
            query = task.text
            if len(query) >= 200:
                query = query[:200].rsplit(" ", 1)[0]
            search_url = self.url_search.format(query.replace(" ", "%20"))

            search_page = 0
            prev_search_results = ""
            while task.answer == "":
                search_page += 1
                search_results = self.get_tasks(search_url + str(search_page))
                if search_results == prev_search_results:
                    break

                for result in search_results:
                    if task.text == result.text and task.images & result.images == task.images:
                        task.task_id = result.task_id
                        if task.solutionLink:
                            task.answer = "Решение: " + self.url_task + str(task.task_id)
                        else:
                            task.answer = result.answer
                        break
                prev_search_results = search_results
        if not task.answer:
            task.answer = "Не найдено"


def main():
    colorama.init()

    url_variant = input('Введите ссылку на вариант с сайта sdamgia : \n')
    cookies = {}

    solver = Solver(url_variant, cookies)

    task_num = 0
    for task in solver.get_tasks(url_variant):
        task_num += 1

        if not task.answer:
            solver.get_answer(task)
        print("{}{}. {}{}".format(Fore.WHITE, task_num, Fore.YELLOW, task.answer))
    print("Готово")


if __name__ == '__main__':
    main()