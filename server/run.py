# -*- coding: utf-8 -*-
"""

"""

from serverviews import server_app
import serverconfig as sc

#server_app.run(debug=sc.DEBUG)
server_app.run(host='0.0.0.0')
