from type_system import *
from program import *

solutions = {
    # singleton (TRANSLATE 0 0 (car var0))
    '1cf80156.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('TRANSLATE'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('car'),[
                Variable(0)
            ])
        ])
    ]),
    # singleton (TRANSLATE 0 0 (max SIZE var0))
    '1f85a75f.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('TRANSLATE'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('max'),[
                BasicPrimitive('SIZE'),
                Variable(0)
            ])
        ])
    ]),
    # singleton (TRANSLATE 0 0 (CHANGE_COLOR (COLOR (max -SIZE var0)) (max SIZE var0)))
    '3de23699.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('TRANSLATE'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('CHANGE_COLOR'),[
                Function(BasicPrimitive('COLOR'),[
                    Function(BasicPrimitive('max'),[
                        Lambda(Function(BasicPrimitive('-'),[
                            Function(BasicPrimitive('SIZE'),[
                                Variable(0)
                            ])
                        ])),
                        Variable(0)
                    ])
                ]),
                Function(BasicPrimitive('max'),[
                    BasicPrimitive('SIZE'),
                    Variable(0)
                ])
            ])
        ])
    ]),
    # ((lambda obj: cons (TRANSLATE 0 ((Y_HIGH obj) + 1) (DUPLICATE obj)) (singleton obj)) (TRANSLATE 0 0 (car var0)))
    '28bf18c6.json': Function(Lambda(
        Function(BasicPrimitive('cons'),[
            Function(BasicPrimitive('TRANSLATE'),[
                BasicPrimitive('0'),
                Function(BasicPrimitive('+_'),[
                    Function(BasicPrimitive('Y_HIGH'),[
                        Variable(0)
                    ]),
                    BasicPrimitive('1_')
                ]),
                Function(BasicPrimitive('DUPLICATE'),[
                    Variable(0)
                ])
            ]),
            Function(BasicPrimitive('singleton'),[
                Variable(0)
            ])
        ])),[
            Function(BasicPrimitive('TRANSLATE'),[
                BasicPrimitive('0'),
                BasicPrimitive('0'),
                Function(BasicPrimitive('car'),[
                    Variable(0)
                ])
            ])
        ]),
    # singleton (TRANSLATE 0 0 (max (lambda obj: length (filter (SAME obj) var1)) var0))
    '39a8645d.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('TRANSLATE'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('max'),[
                Lambda(Function(BasicPrimitive('length'),[
                    Function(BasicPrimitive('filter'),[
                        Function(BasicPrimitive('SAME'),[
                            Variable(0)
                        ]),
                        Variable(1)
                    ])
                ])),
                Variable(0)
            ])
        ])        
    ]),
    # (lambda obj1: (lambda obj2: cons (TRANSLATE ((X_LOW obj2) - 1) ((Y_LOW obj2) - 1) (DUPLICATE obj1)) (singleton obj1))) (max SIZE var0) (max -SIZE var0)
    '88a10436.json': Function(Lambda(Lambda(
        Function(BasicPrimitive('cons'),[
            Function(BasicPrimitive('TRANSLATE'),[
                Function(BasicPrimitive('+_'),[
                    Function(BasicPrimitive('X_LOW'),[
                        Variable(0)
                    ]),
                    Function(BasicPrimitive('-_'),[
                        BasicPrimitive('1_')
                    ])
                ]),
                Function(BasicPrimitive('+_'),[
                    Function(BasicPrimitive('Y_LOW'),[
                        Variable(0)
                    ]),
                    Function(BasicPrimitive('-_'),[
                        BasicPrimitive('1_')
                    ])
                ]),
                Function(BasicPrimitive('DUPLICATE'),[
                    Variable(1)
                ])
            ]),
            Function(BasicPrimitive('singleton'),[
                Variable(1)
            ])
        ]))),
    [
        Function(BasicPrimitive('max'),[
            BasicPrimitive('SIZE'),
            Variable(0)
        ]),
        Function(BasicPrimitive('max'),[
            Lambda(Function(BasicPrimitive('-'),[
                Function(BasicPrimitive('SIZE'),[
                    Variable(0)
                ])
            ])),
            Variable(0)
        ])
    ]),
    # map (lambda obj: CHANGE_COLOR RED (RELATIVE_TRANSLATE 1 0 obj)) var0
    'a79310a0.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('CHANGE_COLOR'),[
            BasicPrimitive('RED'),
            Function(BasicPrimitive('RELATIVE_TRANSLATE'),[
                BasicPrimitive('1_'),
                BasicPrimitive('0'),
                Variable(0)
            ])
        ])),
        Variable(0)
    ]),
    # map (lambda obj: FILL 0 0 1 (SIZE obj) (COLOR obj)) var0
    'd631b094.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('FILL'),[
            BasicPrimitive('0_'),
            BasicPrimitive('0_'),
            BasicPrimitive('1_'),
            Function(BasicPrimitive('SIZE'),[
                Variable(0)
            ]),
            Function(BasicPrimitive('COLOR'),[
                Variable(0)
            ])
        ])),
        Variable(0)
    ]),
    # map (lambda obj: ROTATION90 (ROTATION90 (ROTATION90 var0))) var0
    ######################## need cohesion color
    'ed36ccf7.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('ROTATION90'),[
            Function(BasicPrimitive('ROTATION90'),[
                Function(BasicPrimitive('ROTATION90'),[
                    Variable(0)
                ])
            ])
        ])),
        Variable(0)
    ])
}

cohesions = {
    '1cf80156.json': 'contact',
    '1f85a75f.json': 'contact and color',
    '3de23699.json': 'color',
    '28bf18c6.json': 'contact by point',
    '39a8645d.json': 'contact by point and color',
    '88a10436.json': 'contact',
    'a79310a0.json': 'contact and color',
    'd631b094.json': 'contact by point and color',
    'ed36ccf7.json': 'contact',
}

background_color = {
    '1cf80156.json': 0,
    '1f85a75f.json': 0,
    '3de23699.json': 0,
    '28bf18c6.json': 0,
    '39a8645d.json': 0,
    '88a10436.json': 0,
    'a79310a0.json': 0,
    'd631b094.json': 0,
    'ed36ccf7.json': None,
}

# # map (lambda o: (TRANSLATE 0 ((YCOORD_HIGH o) - (YCOORD_LOW o) + 1) (DUPLICATE (TRANSLATE 0 0 o))) var0
# p_28bf18c6 = Function(BasicPrimitive('cons'),[
#     Function(Lambda(
#         Function(BasicPrimitive('TRANSLATE'),[
#             BasicPrimitive('0'),
#             Function(BasicPrimitive('+'),[
#                 Function(BasicPrimitive('-'),[
#                     Function(BasicPrimitive('YCOORD_HIGH'),[
#                         Variable(0)
#                     ]),
#                     Function(BasicPrimitive('YCOORD_LOW'),[
#                         Variable(0)
#                     ])
#                 ]),
#                 BasicPrimitive('1')
#             ]),
#             Function(BasicPrimitive('DUPLICATE'),[
#                 Function(BasicPrimitive('TRANSLATE'),[
#                     BasicPrimitive('0'),
#                     BasicPrimitive('0'),
#                     Variable(0)
#                 ])
#             ])
#         ])
#     ),[
#         Function(BasicPrimitive('car'),[
#             Variable(0)
#         ])
#     ]),
#     Variable(0)
# ])

# # if (SIZE(ACCESS 1 var0) > SIZE(ACCESS 0 var0)) (TRANSLATE (- XCOORD_LOW(ACCESS 1 var0) 1) -(YCOORD_LOW(ACCESS 1 var0) 1) DUPLICATE(ACCESS 0 var0))
# # (TRANSLATE (- XCOORD_LOW(ACCESS 0 var0) 1) -(YCOORD_LOW(ACCESS 0 var0) 1) DUPLICATE(ACCESS 1 var0))
# p_88a10436 = Function(BasicPrimitive('if'),[
#     Function(BasicPrimitive('gt?'),[
#         Function(BasicPrimitive('SIZE'),[
#             Function(BasicPrimitive('car'),[
#                 Function(BasicPrimitive('car'),[
#                     Variable(0)
#                 ])
#             ])
#         ]),
#         Function(BasicPrimitive('SIZE'),[
#             Function(BasicPrimitive('car'),[
#                 Variable(0)
#             ])
#         ])
#     ]),
#     Function(BasicPrimitive('cons'),[
#         Function(BasicPrimitive('TRANSLATE'),[
#             Function(BasicPrimitive('-'),[
#                 Function(BasicPrimitive('XCOORD_LOW'),[
#                     Function(BasicPrimitive('car'),[
#                         Variable(0)
#                     ])
#                 ]),
#                 BasicPrimitive('1')
#             ]),
#             Function(BasicPrimitive('-'),[
#                 Function(BasicPrimitive('YCOORD_LOW'),[
#                     Function(BasicPrimitive('car'),[
#                         Variable(0)
#                     ])
#                 ]),
#                 BasicPrimitive('1')
#             ]),
#             Function(BasicPrimitive('DUPLICATE'),[
#                 Function(BasicPrimitive('car'),[
#                     Function(BasicPrimitive('car'),[
#                         Variable(0)
#                     ])
#                 ])
#             ])
#         ]),
#         Function(BasicPrimitive('cdr'),[
#             Variable(0)
#         ])
#     ]),
#     Function(BasicPrimitive('cons'),[
#         Function(BasicPrimitive('TRANSLATE'),[
#             Function(BasicPrimitive('-'),[
#                 Function(BasicPrimitive('XCOORD_LOW'),[
#                     Function(BasicPrimitive('car'),[
#                         Function(BasicPrimitive('car'),[
#                             Variable(0)
#                         ])
#                     ])
#                 ]),
#                 BasicPrimitive('1')
#             ]),
#             Function(BasicPrimitive('-'),[
#                 Function(BasicPrimitive('YCOORD_LOW'),[
#                     Function(BasicPrimitive('car'),[
#                         Function(BasicPrimitive('car'),[
#                             Variable(0)
#                         ])
#                     ])
#                 ]),
#                 BasicPrimitive('1')
#             ]),
#             Function(BasicPrimitive('DUPLICATE'),[
#                 Function(BasicPrimitive('car'),[
#                     Variable(0)
#                 ])
#             ])
#         ]),
#         Function(BasicPrimitive('cons'),[
#             Function(BasicPrimitive('car'),[
#                 Variable(0)
#             ]),
#             BasicPrimitive('empty')
#         ])
#     ])
# ])

# # map (lambda o: (lambda i: lambda j: ADD_PIXEL(i,j-1,RED,ADD_PIXEL(i-1,j,...,o)) (XCOORD_LOW o) (YCOORD_LOW o)) var0
# p_d364b489 = Function(BasicPrimitive('map'),[
#     Lambda(
#         Function(Lambda(
#             Function(Lambda(
#                 Function(BasicPrimitive('ADD_PIXEL'),[
#                     Variable(0),
#                     Function(BasicPrimitive('-'),[
#                         Variable(1),
#                         BasicPrimitive('1')
#                     ]),
#                     BasicPrimitive('RED'),
#                     Function(BasicPrimitive('ADD_PIXEL'),[
#                         Function(BasicPrimitive('-'),[
#                             Variable(0),
#                             BasicPrimitive('1')
#                         ]),
#                         Variable(1),
#                         BasicPrimitive('ORANGE'),
#                         Function(BasicPrimitive('ADD_PIXEL'),[
#                             Variable(0),
#                             Function(BasicPrimitive('+'),[
#                                 Variable(1),
#                                 BasicPrimitive('1')
#                             ]),
#                             BasicPrimitive('PINK'),
#                             Function(BasicPrimitive('ADD_PIXEL'),[
#                                 Function(BasicPrimitive('+'),[
#                                     Variable(0),
#                                     BasicPrimitive('1')
#                                 ]),
#                                 Variable(1),
#                                 BasicPrimitive('CYAN'),
#                                 Variable(2)
#                             ])
#                         ])
#                     ])
#                 ]))
#             ,[
#                 Function(BasicPrimitive('XCOORD_LOW'),[
#                     Variable(1)
#                 ])
#             ]))
#         ,[
#             Function(BasicPrimitive('YCOORD_LOW'),[
#                 Variable(0)
#             ])
#         ])
#     ),
#     Variable(0)
# ])

# p_d364b489_aux = Function(BasicPrimitive('map'),[
#     Lambda(
#         Function(Lambda(
#             Function(Lambda(
#                 Function(BasicPrimitive('ADD_PIXEL'),[
#                     Variable(0),
#                     Function(BasicPrimitive('-'),[
#                         Variable(1),
#                         BasicPrimitive('1')
#                     ]),
#                     BasicPrimitive('RED'),
#                     Function(BasicPrimitive('ADD_PIXEL'),[
#                         Function(BasicPrimitive('+'),[
#                             Variable(0),
#                             BasicPrimitive('1')
#                         ]),
#                         Variable(1),
#                         BasicPrimitive('CYAN'),
#                         Variable(2)
#                     ])
#                 ]))
#             ,[
#                 Function(BasicPrimitive('XCOORD_LOW'),[
#                     Variable(1)
#                 ])
#             ]))
#         ,[
#             Function(BasicPrimitive('YCOORD_LOW'),[
#                 Variable(0)
#             ])
#         ])
#     ),
#     Variable(0)
# ])

# p_1cf80156 = Function(BasicPrimitive('map'),[
#     Function(BasicPrimitive('TRANSLATE'),[
#         BasicPrimitive('0'),
#         BasicPrimitive('0')
#     ]),
#     Variable(0)
# ])

# # not working
# p_a87f7484 = Function(BasicPrimitive('filter'),[
#     Lambda(
#         Function(BasicPrimitive('SAME'),[
#             Function(BasicPrimitive('DUPLICATE'),[
#                 Function(BasicPrimitive('TRANSLATE'),[
#                         BasicPrimitive('0'),
#                         BasicPrimitive('0'),
#                         Variable(0)
#                 ])
#             ]),
#             Function(BasicPrimitive('ROTATION90'),[
#                 Function(BasicPrimitive('SYMETRY_X'),[
#                     Variable(0)
#                 ])
#             ])
#         ])
#     ),
#     Variable(0)
# ])