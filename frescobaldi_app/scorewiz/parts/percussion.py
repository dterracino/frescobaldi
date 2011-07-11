# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2011 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
Percussion part types.
"""

import __builtin__

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from . import _base
from . import register



class PitchedPercussionPart(_base.Part):
    """Base class for pitched percussion types."""
    
    
class Timpani(PitchedPercussionPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Timpani")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Timpani", "Tmp.")
        
    midiInstrument = 'timpani'
    clef = 'bass'
    octave = -1


class Xylophone(PitchedPercussionPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Xylophone")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Xylophone", "Xyl.")
        
    midiInstrument = 'xylophone'


class Marimba(PitchedPercussionPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Marimba")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Marimba", "Mar.")
    
    midiInstrument = 'marimba'


class Vibraphone(PitchedPercussionPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Vibraphone")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Vibraphone", "Vib.")
        
    midiInstrument = 'vibraphone'


class TubularBells(PitchedPercussionPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Tubular bells")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Tubular bells", "Tub.")
        
    midiInstrument = 'tubular bells'


class Glockenspiel(PitchedPercussionPart):
    @staticmethod
    def title(_=__builtin__._):
        return _("Glockenspiel")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Glockenspiel", "Gls.")
        
    midiInstrument = 'glockenspiel'


class Drums(_base.Part):
    @staticmethod
    def title(_=__builtin__._):
        return _("Drums")
    
    @staticmethod
    def short(_=__builtin__._):
        return _("abbreviation for Drums", "Dr.")
        
    def createWidgets(self, layout):
        self.voicesLabel = QLabel()
        self.voices = QSpinBox(minimum=1, maximum=4, value=1)
        self.drumStyleLabel = QLabel()
        self.drumStyle = QComboBox()
        self.drumStyle.setModel(DrumStyleModel(self.drumStyle))
        self.drumStems = QCheckBox()
        
        box = QHBoxLayout()
        box.addWidget(self.voicesLabel)
        box.addWidget(self.voices)
        layout.addLayout(box)
        box = QHBoxLayout()
        box.addWidget(self.drumStyleLabel)
        box.addWidget(self.drumStyle)
        layout.addLayout(box)
        layout.addWidget(self.drumStems)
        
    def translateWidgets(self):
        self.voicesLabel.setText(_("Voices:"))
        self.drumStyleLabel.setText(_("Style:"))
        self.drumStems.setText(_("Remove stems"))
        self.drumStems.setToolTip(_("Remove the stems from the drum notes."))
        self.drumStyle.update()


class DrumStyleModel(QAbstractListModel):
    _data = (
        lambda: _("Drums (5 lines, default)"),
        lambda: _("Timbales-style (2 lines)"),
        lambda: _("Congas-style (2 lines)"),
        lambda: _("Bongos-style (2 lines)"),
        lambda: _("Percussion-style (1 line)"),
    )
    
    def rowCount(self, parent):
        return len(self._data)
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]()


register(
    lambda: _("Percussion"),
    [
        Timpani,
        Xylophone,
        Marimba,
        Vibraphone,
        TubularBells,
        Glockenspiel,
        Drums,
    ])
