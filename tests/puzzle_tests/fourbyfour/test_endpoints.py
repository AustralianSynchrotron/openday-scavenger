from fastapi import status
from fastapi.testclient import TestClient

from openday_scavenger.puzzles.fourbyfour.service import PuzzleStatus, get_parsed_solution

PREFIX = "/puzzles"
PUZZLE_NAME = "fourbyfour"


class TestFourByFour:
    def test_index(self, mock_init_client: TestClient) -> None:
        response = mock_init_client.get(f"{PREFIX}/{PUZZLE_NAME}")
        assert response.status_code == status.HTTP_200_OK
        assert hasattr(response, "context")

    def test_get_shuffled_words(self, mock_init_client: TestClient, mocker) -> None:
        _spy = mocker.spy(PuzzleStatus, "shuffle_words")

        response = mock_init_client.get(f"{PREFIX}/{PUZZLE_NAME}/shuffled")
        assert response.status_code == status.HTTP_200_OK
        assert hasattr(response, "context")
        _spy.assert_called_once()

    def test_deselect_all_words(self, mock_init_client: TestClient, mocker) -> None:
        _spy = mocker.spy(PuzzleStatus, "deselect_all_words")

        response = mock_init_client.delete(f"{PREFIX}/{PUZZLE_NAME}/selection")
        assert response.status_code == status.HTTP_200_OK
        assert hasattr(response, "context")
        _spy.assert_called_once()

    def test_toggle_word_selection(self, mock_init_client: TestClient, mocker) -> None:
        _spy = mocker.spy(PuzzleStatus, "toggle_word_selection")
        solution = get_parsed_solution()
        a_word = next(iter(solution[next(iter(solution.keys()))]))

        response = mock_init_client.put(f"{PREFIX}/{PUZZLE_NAME}/{a_word}/selection")
        assert response.status_code == status.HTTP_200_OK
        assert hasattr(response, "context")
        ss = response.context["status"]
        assert ss.get_word(a_word).is_selected
        _spy.assert_called_once()

    def test_get_static_files_parametrized(
        self,
        mock_init_client: TestClient,
    ) -> None:
        response = mock_init_client.get(f"{PREFIX}/{PUZZLE_NAME}/static/styles.css")
        assert response.status_code == status.HTTP_200_OK

    def test_get_static_files_not_found_parametrized(
        self,
        mock_init_client: TestClient,
    ) -> None:
        response = mock_init_client.get(f"{PREFIX}/{PUZZLE_NAME}/static/foo.bar")
        assert "404" in response.content.decode("utf-8")
        # TODO: change to next line if the custom_exception_handler is updated to return a 404 status
        # assert response.status_code == status.HTTP_404_NOT_FOUND
