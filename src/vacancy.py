
class Vacancy:
    """Класс для представления Вакансии"""
    __slots__ = ("name", "area", "salary_from", "salary_to", "requirement", "responsibility", "schedule", "url")

    def __init__(
            self,
            name: str,
            area: str| None,
            salary_from: int | None,
            salary_to: int | None,
            requirement: str | None,
            responsibility: str| None,
            schedule: str| None,
            url: str
    ):
        self.name = name                        # Название вакансии
        self.area = area                        # Город
        self.salary_from = salary_from          # Зарплата от
        self.salary_to = salary_to              # Зарплата до
        self.requirement = requirement          # Требования
        self.responsibility = responsibility    # Обязанности
        self.schedule = schedule                # График работы
        self.url = url                          # Ссылка на вакансию

    def __lt__(self, other: "Vacancy") -> bool:
        """Сравнение вакансий по зарплате """
        return (self.salary_from or 0) < (other.salary_from or 0)


    def __eq__(self, other: "Vacancy") -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.salary_from == other.salary_from


    @classmethod
    def from_vacancy_hh(cls, hh_data: dict) -> "Vacancy":
        salary = hh_data.get("salary") or {}

        return cls(
            name=hh_data.get("name"),
            area=hh_data.get("area", {}).get("name"),
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            requirement=hh_data.get("snippet", {}).get("requirement"),
            responsibility=hh_data.get("snippet", {}).get("responsibility"),
            schedule=hh_data.get("schedule", {}).get("name"),
            url=hh_data.get("alternate_url"),

        )


