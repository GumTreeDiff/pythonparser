// Copyright (c) Aniskov N.

fun printProduct(arg1: String, arg2: String) {
    val x = parseInt(arg1)
    val y = parseInt(arg2)

    if (x != null && y != null) {
        println(x * y)
    }
    else {
        println("'$arg1' or '$arg2' is not a number")
    }    
}