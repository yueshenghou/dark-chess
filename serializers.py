import logging

from flask import jsonify

from consts import FIGURES, COLORS, UNKNOWN
from helpers import pos2coors


logger = logging.getLogger(__name__)


class BaseSerializer(object):

    def __init__(self, model, color=UNKNOWN):
        self._model = model
        self._color = color

    def calc(self):
        return self._model

    def to_json(self):
        try:
            data = self.calc()
            if 'rc' not in data:
                data['rc'] = True
            return jsonify(data)
        except Exception as exc:
            logger.error(exc)
            return jsonify({'rc': False, 'error': 'system error'})


class FigureSerializer(BaseSerializer):

    def calc(self):
        if not self._model:
            return {}
        return {
            'kind': FIGURES[self._model.kind],
            'color': COLORS[self._model.color],
            'position': pos2coors(self._model.x, self._model.y),
            'moves': [pos2coors(*m) for m in self._model.getMoves()],
        }


class BoardSerializer(BaseSerializer):

    def calc(self):
        data = {}
        if self._color == UNKNOWN:
            raise AttributeError('color is not specified')
        figures = filter(lambda a: a.color == self._color, self._model.figures)
        moves = reduce(lambda a, b: a + b, [f.getMoves() for f in figures])
        for cell in moves:
            data[pos2coors(*cell)] = FigureSerializer(self._model.cell2Figure(*cell)).calc()
        for fig in figures:
            data[pos2coors(fig.x, fig.y)] = FigureSerializer(fig).calc()
        return data


class GameSerializer(BaseSerializer):

    def calc(self):
        return {
            'moves': [('{}{}'.format(m['figure'].symbol, pos2coors(m['x1'], m['y1'])), pos2coors(m['x2'], m['y2'])) for m in self._model.moves]
        }


def send_data(data):
    return BaseSerializer(data).to_json()


def send_message(message):
    return send_data({'message': message})


def send_error(error):
    return send_data({'rc': False, 'error': error})


def send_success():
    return send_data({'rc': True})