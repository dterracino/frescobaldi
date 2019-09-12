# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
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
A widget and dialog to show an output preview of a LilyPond document.
"""


from PyQt5.QtCore import (
    QSize,
    Qt
)
from PyQt5.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QHBoxLayout,
                             QLabel, QStackedLayout, QVBoxLayout, QWidget)

import app
import icons
import job
import log
import qutil
import popplerview
import popplertools
import widgets.progressbar


class MusicPreviewWidget(QWidget):
    def __init__(
        self,
        parent=None,
        showProgress=True,
        showWaitingCursor=False,
        progressHidden=False,
        progressHiddenWhileIdle=True,
        progressShowFinished=3000,
        showLog=True
    ):
        super(MusicPreviewWidget, self).__init__(parent)
        self._lastbuildtime = 10.0
        self._running = None
        self._current = None

        self._showLog = showLog
        if showLog:
            self._log = log.Log()
        self._showProgress = showProgress
        self._showWaitingCursor = showWaitingCursor

        self._chooserLabel = QLabel()
        self._chooser = QComboBox(self, activated=self.selectDocument)
        self._view = popplerview.View()

        self._stack = QStackedLayout()
        self._top = QWidget()

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self._top)
        layout.addLayout(self._stack)
        if self._showProgress:
            self._progress = widgets.progressbar.TimedProgressBar(
                parent=self,
                hidden=progressHidden,
                hideWhileIdle=progressHiddenWhileIdle,
                showFinished=progressShowFinished
            )
            layout.addWidget(self._progress)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(2)
        self._top.setLayout(top)
        top.addWidget(self._chooserLabel)
        top.addWidget(self._chooser)
        top.addStretch(1)

        if showLog:
            self._stack.addWidget(self._log)
        self._stack.addWidget(self._view)

        self._top.hide()
        app.aboutToQuit.connect(self.cleanup)
        app.translateUI(self)

    def translateUI(self):
        self._chooserLabel.setText(_("Document:"))

    def preview(
        self, text, title=None, base_dir=None,
        temp_dir='', cached=False
    ):
        """Runs LilyPond on the given text and shows the resulting PDF."""
        self.cleanup_running()
        if cached:
            self._running = j = job.lilypond.CachedPreviewJob(
                text,
                target_dir=temp_dir,
                base_dir=base_dir,
                title=title
            )
            if not self._running.needs_compilation():
                self._done(None)
                return
        else:
            self._running = j = job.lilypond.VolatileTextJob(
                text,
                title=title
            )
        j.done.connect(self._done)
        if self._showLog:
            self._log.clear()
            self._log.connectJob(j)
            self._stack.setCurrentWidget(self._log)
        if self._showProgress:
            j.started.connect(
                lambda: self._progress.start(self._lastbuildtime)
            )
            self._progress.start(self._lastbuildtime)
        if self._showWaitingCursor:
            j.started.connect(
                lambda: app.qApp.setOverrideCursor(Qt.WaitCursor)
            )
        app.job_queue().add_job(j, 'generic')

    def _done(self, success):
        # TODO: Handle failed compilation (= no file to show)
        if self._showProgress:
            self._progress.stop()
        pdfs = self._running.resultfiles()
        self.setDocuments(pdfs)
        if not pdfs and self._showLog:
            self._stack.setCurrentWidget(self._log)
            return
        self._lastbuildtime = self._running.elapsed_time()
        self._stack.setCurrentWidget(self._view)
        if self._current:
            self._current.cleanup()
        self._current = self._running  # keep the tempdir
        self._running = None

    def setDocuments(self, pdfs):
        """Loads the given PDF path names in the UI."""
        self._documents = [popplertools.Document(name) for name in pdfs]
        self._chooser.clear()
        self._chooser.addItems([d.name() for d in self._documents])
        self._top.setVisible(len(self._documents) > 1)
        if pdfs:
            self._chooser.setCurrentIndex(0)
            self.selectDocument(0)
        else:
            self._view.clear()

    def selectDocument(self, index):
        doc = self._documents[index].document()
        if doc:
            self._view.load(doc)

    def cleanup(self):
        if self._running:
            self._running.abort()
            self._running.cleanup()
            self._running = None
        if self._current:
            self._current.cleanup()
            self._current = None
        if self._showLog:
            self._stack.setCurrentWidget(self._log)
        self._top.hide()
        self._view.clear()

    def print_(self):
        """Prints the currently displayed document."""
        if self._documents:
            doc = self._documents[self._chooser.currentIndex()]
            import popplerprint
            popplerprint.printDocument(doc, self)


class MusicPreviewDialog(QDialog):
    def __init__(self, parent=None):
        super(MusicPreviewDialog, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self._widget = MusicPreviewWidget()
        layout.addWidget(self._widget)
        layout.addWidget(widgets.Separator())
        b = QDialogButtonBox()
        layout.addWidget(b)
        b.addButton(QDialogButtonBox.Close)
        b.rejected.connect(self.accept)
        self._printButton = b.addButton('', QDialogButtonBox.ActionRole)
        self._printButton.setIcon(icons.get("document-print"))
        self._printButton.clicked.connect(self._widget.print_)
        self._printButton.hide()
        qutil.saveDialogSize(self, "musicpreview/dialog/size", QSize(500, 350))
        app.translateUI(self)

    def translateUI(self):
        self._printButton.setText(_("&Print"))
        self.setWindowTitle(app.caption(_("Music Preview")))

    def preview(self, text, title=None):
        self._widget.preview(text, title)

    def cleanup(self):
        self._widget.cleanup()

    def setEnablePrintButton(self, enable):
        """Enables or disables the print button."""
        self._printButton.setVisible(enable)
