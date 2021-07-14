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
                Function(BasicPrimitive('+'),[
                    Function(BasicPrimitive('Y_HIGH'),[
                        Variable(0)
                    ]),
                    BasicPrimitive('1')
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
                Function(BasicPrimitive('+'),[
                    Function(BasicPrimitive('X_LOW'),[
                        Variable(0)
                    ]),
                    Function(BasicPrimitive('-'),[
                        BasicPrimitive('1')
                    ])
                ]),
                Function(BasicPrimitive('+'),[
                    Function(BasicPrimitive('Y_LOW'),[
                        Variable(0)
                    ]),
                    Function(BasicPrimitive('-'),[
                        BasicPrimitive('1')
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
                BasicPrimitive('1'),
                BasicPrimitive('0'),
                Variable(0)
            ])
        ])),
        Variable(0)
    ]),
    # map (lambda obj: FILL 0 0 0 (+ (SIZE obj) -1) (COLOR obj)) var0
    'd631b094.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('FILL'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('+'),[
                Function(BasicPrimitive('SIZE'),[
                    Variable(0)
                ]),
                Function(BasicPrimitive('-'),[
                    BasicPrimitive('1')
                ])
            ]),
            Function(BasicPrimitive('COLOR'),[
                Variable(0)
            ])
        ])),
        Variable(0)
    ]),
    # map (lambda obj: ROTATION90 (ROTATION90 (ROTATION90 var0))) var0
    'ed36ccf7.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('ROTATION90'),[
            Variable(0)
        ])),
        Variable(0)
    ]),
    # map (lambda obj: if ((COLOR obj) == GRAY) (CHANGE_COLOR ORANGE (DUPLICATE var0)) var0) var0
    'c8f0f002.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('if'),[
            Function(BasicPrimitive('eq?'),[
                Function(BasicPrimitive('COLOR'),[
                    Variable(0)
                ]),
                BasicPrimitive('ORANGE')
            ]),
            Function(BasicPrimitive('CHANGE_COLOR'),[
                BasicPrimitive('GRAY'),
                Function(BasicPrimitive('DUPLICATE'),[
                    Variable(0)
                ])
            ]),
            Variable(0)
        ])),
        Variable(0)
    ]),
    # singleton (SYMETRY_Y (ROT90 (car var0)))
    '74dd1130.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('SYMETRY_X'),[
            Function(BasicPrimitive('ROTATION90'),[
                Function(BasicPrimitive('car'),[
                    Variable(0)
                ])
            ])
        ])
    ]),
    # filter (lambda obj: SAME (SYMETRY_Y obj) (TRANSLATE 0 0 obj)) var0
    '72ca375d.json': Function(BasicPrimitive('filter'),[
        Lambda(Function(BasicPrimitive('SAME'),[
            Function(BasicPrimitive('SYMETRY_Y'),[
                Function(BasicPrimitive('DUPLICATE'),[
                    Variable(0)
                ])
            ]),
            Function(BasicPrimitive('TRANSLATE'),[
                BasicPrimitive('0'),
                BasicPrimitive('0'),
                Variable(0)
            ])
        ])),
        Variable(0)
    ]),
    # map (lambda obj: if (SAME obj (max SIZE var1)) (CHANGE_COLOR BLUE (DUPLICATE obj)) (if (SAME obj (max -SIZE var1)) (CHANGE_COLOR RED (DUPLICATE obj)) obj)) (map (CHANGE_COLOR YELLOW) var0)
    'ea32f347.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('if'),[
            Function(BasicPrimitive('SAME'),[
                Variable(0),
                Function(BasicPrimitive('max'),[
                    BasicPrimitive('SIZE'),
                    Variable(1)
                ])
            ]),
            Function(BasicPrimitive('CHANGE_COLOR'),[
                BasicPrimitive('BLUE'),
                Function(BasicPrimitive('DUPLICATE'),[
                    Variable(0)
                ])
            ]),
            Function(BasicPrimitive('if'),[
                Function(BasicPrimitive('SAME'),[
                    Variable(0),
                    Function(BasicPrimitive('max'),[
                        Lambda(Function(BasicPrimitive('-'),[
                            Function(BasicPrimitive('SIZE'),[
                                Variable(0)
                            ])
                        ])),
                        Variable(1)
                    ])
                ]),
                Function(BasicPrimitive('CHANGE_COLOR'),[
                    BasicPrimitive('RED'),
                    Function(BasicPrimitive('DUPLICATE'),[
                        Variable(0)
                    ])
                ]),
                Variable(0)
            ])
        ])),
        Function(BasicPrimitive('map'),[
            Function(BasicPrimitive('CHANGE_COLOR'),[
                BasicPrimitive('YELLOW')
            ]),
            Variable(0)
        ])
    ]),
    # singleton (TRANSLATE 0 0 (max SIZE var0))
    'be94b721.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('TRANSLATE'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('max'),[
                BasicPrimitive('SIZE'),
                Variable(0)
            ])
        ])
    ]),
    # map (lambda obj: if (SAME obj (max SIZE var1)) ((lambda obj1: TRANSLATE ((X_LOW obj1) + 1) ((Y_LOW obj1) + 1) (DUPLICATE obj)) (max -SIZE var1)) var0) var0
    'a1570a43.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('if'),[
            Function(BasicPrimitive('SAME'),[
                Variable(0),
                Function(BasicPrimitive('max'),[
                    BasicPrimitive('SIZE'),
                    Variable(1)
                ])
            ]),
            Function(Lambda(Function(BasicPrimitive('TRANSLATE'),[
                    Function(BasicPrimitive('+'),[
                        Function(BasicPrimitive('X_LOW'),[
                            Variable(0)
                        ]),
                        BasicPrimitive('1')
                    ]),
                    Function(BasicPrimitive('+'),[
                        Function(BasicPrimitive('Y_LOW'),[
                            Variable(0)
                        ]),
                        BasicPrimitive('1')
                    ]),
                    Function(BasicPrimitive('DUPLICATE'),[
                        Variable(1)
                    ])
                ])),[
                Function(BasicPrimitive('max'),[
                    Lambda(Function(BasicPrimitive('-'),[
                        Function(BasicPrimitive('SIZE'),[
                            Variable(0)
                        ])
                    ])),
                    Variable(1)
                ])
            ]),
            Variable(0)
        ])),
        Variable(0)
    ]),
    # singleton (TRANSLATE 0 0 (SYMETRY_Y (car var0)))
    '7468f01a.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('TRANSLATE'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('SYMETRY_Y'),[
                Function(BasicPrimitive('car'),[
                    Variable(0)
                ])
            ])
        ])
    ]),
    # singleton (FILL 0 0 2 2 (COLOR (max SIZE va0)))
    '5582e5ca.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('FILL'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('+'),[
                BasicPrimitive('1'),
                BasicPrimitive('1')
            ]),
            Function(BasicPrimitive('+'),[
                BasicPrimitive('1'),
                BasicPrimitive('1')
            ]),
            Function(BasicPrimitive('COLOR'),[
                Function(BasicPrimitive('max'),[
                    BasicPrimitive('SIZE'),
                    Variable(0)
                ])
            ])
        ])
    ]),
    # singleton (ROT90 (ROT90 (car var0)))
    '3c9b0459.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('ROTATION90'),[
            Function(BasicPrimitive('ROTATION90'),[
                Function(BasicPrimitive('car'),[
                    Variable(0)
                ])
            ])
        ])
    ]),
    # map (lambda obj: if ((COLOR obj) == PINK) (CHANGE_COLOR RED (DUPLICATE obj)) obj) var0
    'b1948b0a.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('if'),[
            Function(BasicPrimitive('eq?'),[
                Function(BasicPrimitive('COLOR'),[
                    Variable(0)
                ]),
                BasicPrimitive('PINK')
            ]),
            Function(BasicPrimitive('CHANGE_COLOR'),[
                BasicPrimitive('RED'),
                Function(BasicPrimitive('DUPLICATE'),[
                    Variable(0)
                ])
            ]),
            Variable(0)
        ])),
        Variable(0)
    ]),
    # singleton (CHANGE_COLOR (COLOR (max -SIZE var0)) (max SIZE var0))
    'aabf363d.json': Function(BasicPrimitive('singleton'),[
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
    ]),
    # singleton (FILL 0 0 0 (+ (length (filter (lambda obj: (SIZE obj) > 1) (filter (lambda obj: (COLOR obj) == BLUE) var0))) -1) BLUE)
    '1fad071e.json': Function(BasicPrimitive('singleton'),[
        Function(BasicPrimitive('FILL'),[
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            BasicPrimitive('0'),
            Function(BasicPrimitive('+'),[
                Function(BasicPrimitive('length'),[
                    Function(BasicPrimitive('filter'),[
                        Lambda(Function(BasicPrimitive('gt?'),[
                            Function(BasicPrimitive('SIZE'),[
                                Variable(0)
                            ]),
                            BasicPrimitive('1')
                        ])),
                        Function(BasicPrimitive('filter'),[
                            Lambda(Function(BasicPrimitive('eq?'),[
                                Function(BasicPrimitive('COLOR'),[
                                    Variable(0)
                                ]),
                                BasicPrimitive('BLUE')
                            ])),
                            Variable(0)
                        ])
                    ])
                ]),
                Function(BasicPrimitive('-'),[
                    BasicPrimitive('1')
                ])
            ]),
            BasicPrimitive('BLUE')
        ])
    ]),
    # map (lambda obj: if ((COLOR obj) == GRAY) (CHANGE_COLOR CYAN (DUPLICATE obj)) (if ((COLOR obj) == CYAN) (CHANGE_COLOR GRAY (DUPLICATE obj)) obj) var0
    'd511f180.json': Function(BasicPrimitive('map'),[
        Lambda(Function(BasicPrimitive('if'),[
            Function(BasicPrimitive('eq?'),[
                Function(BasicPrimitive('COLOR'),[
                    Variable(0)
                ]),
                BasicPrimitive('GRAY')
            ]),
            Function(BasicPrimitive('CHANGE_COLOR'),[
                BasicPrimitive('CYAN'),
                Function(BasicPrimitive('DUPLICATE'),[
                    Variable(0)
                ])
            ]),
            Function(BasicPrimitive('if'),[
                Function(BasicPrimitive('eq?'),[
                    Function(BasicPrimitive('COLOR'),[
                        Variable(0)
                    ]),
                    BasicPrimitive('CYAN')
                ]),
                Function(BasicPrimitive('CHANGE_COLOR'),[
                    BasicPrimitive('GRAY'),
                    Function(BasicPrimitive('DUPLICATE'),[
                        Variable(0)
                    ])
                ]),
                Variable(0)
            ])
        ])),
        Variable(0)
    ]),
    # (lambda f: if ((length (filter f (map (TRANSLATE 0 0) var1))) > 1) (filter (lambda obj: not (f obj)) var1) (filter f var1)) (lambda obj: SAME (SYMETRY_X (ROT90 (DUPLICATE obj))) obj)
    'a87f7484.json': Function(Lambda(Function(BasicPrimitive('if'),[
            Function(BasicPrimitive('gt?'),[
                Function(BasicPrimitive('length'),[
                    Function(BasicPrimitive('filter'),[
                        Variable(0),
                        Function(BasicPrimitive('map'),[
                            Function(BasicPrimitive('TRANSLATE'),[
                                BasicPrimitive('0'),
                                BasicPrimitive('0')
                            ]),
                            Variable(1)
                        ])
                    ])
                ]),
                BasicPrimitive('1')
            ]),
            Function(BasicPrimitive('filter'),[
                Lambda(Function(BasicPrimitive('not'),[
                    Function(Variable(1),[
                        Variable(0)
                    ])
                ])),
                Variable(1)
            ]),
            Function(BasicPrimitive('filter'),[
                Variable(0),
                Variable(1)
            ])
    ])),[
        Lambda(Function(BasicPrimitive('SAME'),[
            Function(BasicPrimitive('SYMETRY_X'),[
                Function(BasicPrimitive('ROTATION90'),[
                    Function(BasicPrimitive('DUPLICATE'),[
                        Variable(0)
                    ])
                ])
            ]),
            Variable(0)]))
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
    'c8f0f002.json': 'color',
    '74dd1130.json': 'contact',
    '72ca375d.json': 'contact by point and color',
    'ea32f347.json': 'contact and color',
    'be94b721.json': 'contact and color',
    'a1570a43.json': 'color',
    '7468f01a.json': 'contact',
    '5582e5ca.json': 'color',
    '3c9b0459.json': 'contact',
    'b1948b0a.json': 'color',
    'aabf363d.json': 'contact and color',
    '1fad071e.json': 'contact and color',
    'd511f180.json': 'color',
    'a87f7484.json': 'contact by point and color',
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
    'c8f0f002.json': 0,
    '74dd1130.json': 0,
    '72ca375d.json': 0,
    'ea32f347.json': 0,
    'be94b721.json': 0,
    'a1570a43.json': 0,
    '7468f01a.json': 0,
    '5582e5ca.json': 0,
    '3c9b0459.json': 0,
    'b1948b0a.json': 0,
    'aabf363d.json': 0,
    '1fad071e.json': 0,
    'd511f180.json': 0,
    'a87f7484.json': 0,
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