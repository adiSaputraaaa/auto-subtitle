function favorite(e, s, t) {
  is_login
    ? ("undefined" == typeof t && (t = "add"),
      $(".btn-favorite-" + e).prop("disabled", !0),
      $(".bp-btn-like").prop("disabled", !0),
      $.ajax({
        url: base_url + "ajax/user_favorite",
        method: "POST",
        data: { movie_id: e, action: t },
        dataType: "json",
        success: function (t) {
          ($(".btn-favorite-" + e).removeAttr("disabled"),
            $(".bp-btn-like").removeAttr("disabled"),
            1 == t.status &&
              (1 == s
                ? ($("#message-content").html(t.message),
                  $("#pop-alert").modal("show"),
                  "user" == window.location.pathname.split("/")[1] &&
                    $("[data-movie-id=" + e + "]").addClass("ml-item-remove"))
                : ($("#favorite-alert").show(),
                  $("#favorite-message").html(t.message),
                  setTimeout(function () {
                    $("#favorite-alert").hide();
                  }, 5e3),
                  $("#button-favorite").html(t.content),
                  $(".popover-like").hide())));
        },
      }))
    : $("#pop-login").modal("show");
}
function goRequestPage(e) {
  is_login ? (window.location.href = e) : $("#pop-login").modal("show");
}
function clearNotify() {
  var e = confirm("Are you sure delete all notify?");
  e &&
    $.ajax({
      url: base_url + "ajax/user_clear_notify",
      method: "POST",
      dataType: "json",
      success: function (e) {
        1 == e.status && window.location.reload();
      },
    });
}
function loadNotify() {
  0 == $("#list-notify .notify-item").length &&
    $.ajax({
      url: base_url + "ajax/user_load_notify",
      type: "GET",
      dataType: "json",
      success: function (e) {
        1 == e.status &&
          ($("#notify-loading").remove(),
          $("#list-notify").html(e.html),
          e.notify_unread > 0
            ? $(".feed-number").text(e.notify_unread)
            : $(".feed-number").text(""));
      },
    });
}
function ajaxContentBox(r) {
  $("div#" + r + " #content-box").is(":empty") &&
    $.ajax({
      url: base_url + "ajax/get_content_box/" + r,
      type: "GET",
      dataType: "json",
      success: function (e) {
        switch (e.type) {
          case "topview-today":
            $("#topview-today #content-box").html(e.content);
            break;
          case "top-favorite":
            $("#top-favorite #content-box").html(e.content);
            break;
          case "top-rating":
            $("#top-rating #content-box").html(e.content);
            break;
          case "top-imdb":
            $("#top-imdb #content-box").html(e.content);
        }
      },
    });
}
function updateMovieView(e) {
  $.cookie("view-" + e) ||
    $.ajax({
      url: base_url + "ajax/movie_update_view",
      type: "POST",
      dataType: "json",
      data: { id: e },
      success: function () {
        var s = new Date(),
          t = 2;
        (s.setTime(s.getTime() + 60 * t * 1e3),
          $.cookie("view-" + e, !0, { expires: s, path: "/" }));
      },
    });
}
function validateEmail(e) {
  var s = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
  return e.length > 0 && s.test(e);
}
function subscribe() {
  if (!$.cookie("subscribed")) {
    $("#error-email-subs").hide();
    var e = $("input[name=email]").val();
    "" == e.trim()
      ? ($("#error-email-subs").text("Please enter your email."),
        $("#error-email-subs").show())
      : validateEmail(e)
        ? ($("#subscribe-submit").prop("disabled", !0),
          $("#subscribe-loading").show(),
          $.ajax({
            url: base_url + "site/subscribe",
            type: "POST",
            dataType: "json",
            data: { email: e },
            success: function (e) {
              (1 == e.status &&
                ($("#pop-subc").modal("hide"),
                $.cookie("subscribed", 1, { expires: 365, path: "/" }),
                $.cookie("subscribe", 1, { expires: 365, path: "/" })),
                $("#subscribe-loading").hide(),
                $("#subscribe-submit").removeAttr("disabled"));
            },
          }))
        : ($("#error-email-subs").text("Please enter a valid email."),
          $("#error-email-subs").show());
  }
}
function subscribe_home() {
  if (!$.cookie("subscribed")) {
    ($("#error-email-subs").hide(), $("#success-subs").hide());
    var e = $("input[name=email-home]").val();
    "" == e.trim()
      ? ($("#error-email-subs").text("Please enter your email."),
        $("#error-email-subs").show())
      : validateEmail(e)
        ? ($("#subscribe-submit-home").prop("disabled", !0),
          $.ajax({
            url: base_url + "site/subscribe",
            type: "POST",
            dataType: "json",
            data: { email: e },
            success: function (e) {
              (1 == e.status
                ? ($("#success-subs").text("Thank you for subscribing!"),
                  $("#success-subs").show(),
                  $.cookie("subscribed", 1, { expires: 365, path: "/" }),
                  $.cookie("subscribe", 1, { expires: 365, path: "/" }))
                : ($("#error-email-subs").text("Subscribe failed."),
                  $("#error-email-subs").show()),
                $("#subscribe-submit-home").removeAttr("disabled"));
            },
          }))
        : ($("#error-email-subs").text("Please enter a valid email."),
          $("#error-email-subs").show());
  }
}
function subscribe_footer() {
  if (!$.cookie("subscribed")) {
    ($("#error-email-subs-footer").hide(), $("#success-subs-footer").hide());
    var e = $("input[name=email-footer]").val();
    "" == e.trim()
      ? ($("#error-email-subs-footer").text("Please enter your email."),
        $("#error-email-subs-footer").show())
      : validateEmail(e)
        ? ($("#subscribe-submit-footer").prop("disabled", !0),
          $.ajax({
            url: base_url + "site/subscribe",
            type: "POST",
            dataType: "json",
            data: { email: e },
            success: function (e) {
              (1 == e.status
                ? ($("#success-subs-footer").text("Thank you for subscribing!"),
                  $("#success-subs-footer").show(),
                  $.cookie("subscribed", 1, { expires: 365, path: "/" }),
                  $.cookie("subscribe", 1, { expires: 365, path: "/" }))
                : ($("#error-email-subs-footer").text("Subscribe failed."),
                  $("#error-email-subs-footer").show()),
                $("#subscribe-submit-footer").removeAttr("disabled"));
            },
          }))
        : ($("#error-email-subs-footer").text("Please enter a valid email."),
          $("#error-email-subs-footer").show());
  }
}
function isCookieEnabled() {
  var e = !!navigator.cookieEnabled;
  return (
    "undefined" != typeof navigator.cookieEnabled ||
      e ||
      ((document.cookie = "testcookie"),
      (e = -1 != document.cookie.indexOf("testcookie"))),
    e
  );
}
function searchMovie() {
  var e = $("input[name=keyword]").val();
  "" !== e.trim() &&
    ((e = e
      .replace(/(<([^>]+)>)/gi, "")
      .replace(/[`~!@#$%^&*()_|\=?;:'",.<>\{\}\[\]\\\/]/gi, "")),
    (e = e.split(" ").join(" ")),
    (window.location.href = base_url + "search/" + e));
}
var base_url = "http://" + document.domain + "/",
  is_login = !1,
  s7euu24fblrg914z = "x6a4moj7q8xq6dk5";
($(document).ready(function () {
  function e() {
    $(this).find(".sub-container").css("display", "block");
  }
  function s() {
    $(this).find(".sub-container").css("display", "none");
  }
  /*$.ajax({url:base_url+"ajax/load_login_status",type:"GET",dataType:"json",success:function(e){$("#top-user").html(e.content),1==e.is_login&&(is_login=!0)}}),*/ ($(
    "#search a.box-title",
  ).click(function () {
    $("#search .box").toggleClass("active");
  }),
    $(".mobile-menu").click(function () {
      ($("#menu,.mobile-menu").toggleClass("active"),
        $("#search, .mobile-search").removeClass("active"));
    }),
    $(".mobile-search").click(function () {
      ($("#search,.mobile-search").toggleClass("active"),
        $("#menu, .mobile-menu").removeClass("active"));
    }),
    $(".filter-toggle").click(function () {
      ($("#filter").toggleClass("active"),
        $(".filter-toggle").toggleClass("active"));
    }),
    $(".bp-btn-light").click(function () {
      $(
        ".bp-btn-light, #overlay, #media-player, #content-embed, #comment-area",
      ).toggleClass("active");
    }),
    $("#overlay").click(function () {
      $(
        ".bp-btn-light, #overlay, #media-player, #content-embed, #comment-area",
      ).removeClass("active");
    }),
    $(".bp-btn-auto").click(function () {
      $(".bp-btn-auto").toggleClass("active");
    }),
    $("#toggle, .cac-close").click(function () {
      $("#comment").toggleClass("active");
    }),
    $(".top-menu> li").bind("mouseover", e),
    $(".top-menu> li").bind("mouseout", s));
  var t = 0;
  ($(window).on("scroll", function () {
    ($(window).scrollTop() < t
      ? "fixed" != $("header").css("position") &&
        ($("header").css({
          position: "fixed",
          top: -$("header").outerHeight(),
          backgroundColor: "#fff",
        }),
        $("header").animate({ top: "0px" }, 500),
        $("#main").css("padding-top", $("header").outerHeight()))
      : ($("header").css({ position: "relative", top: "0px" }),
        $("#main").css("padding-top", "0px")),
      (t = $(window).scrollTop()));
  }),
    $(function () {
      function e() {
        var e = $(this),
          s = e.find(".modal-dialog");
        (e.css("display", "block"),
          s.css(
            "margin-top",
            Math.max(0, ($(window).height() - s.height()) / 2),
          ));
      }
      ($(".modal").on("show.bs.modal", e),
        $(window).on("resize", function () {
          $(".modal:visible").each(e);
        }));
    }));
  var o = !0;
  ($(".search-suggest").mouseover(function () {
    o = !1;
  }),
    $(".search-suggest").mouseout(function () {
      o = !0;
    }),
    $("input[name=keyword]").keyup(function () {
      var e = $(this).val(),
        s = md5(e + s7euu24fblrg914z);
      e.trim().length > 2
        ? $.ajax({
            url: base_url + "ajax/suggest_search",
            type: "POST",
            dataType: "json",
            data: { keyword: e, token: s },
            success: function (e) {
              ($(".search-suggest").html(e.content),
                "" !== e.content.trim()
                  ? $(".search-suggest").show()
                  : $(".search-suggest").hide());
            },
          })
        : $(".search-suggest").hide();
    }),
    $("input[name=keyword]").blur(function () {
      o && $(".search-suggest").hide();
    }),
    $("input[name=keyword]").focus(function () {
      "" !== $(".search-suggest").html() && $(".search-suggest").show();
    }),
    $("input[name=keyword]").keypress(function (e) {
      13 == e.which && searchMovie();
    }),
    $("#login-form").submit(function (e) {
      ($("#login-submit").prop("disabled", !0), $("#login-loading").show());
      var s = $(this).serializeArray(),
        t = $(this).attr("action");
      ($.ajax({
        url: t,
        type: "POST",
        data: s,
        dataType: "json",
        success: function (e) {
          (0 == e.status &&
            ($("#error-message").show(),
            $("#error-message").text(e.message),
            $("#login-submit").removeAttr("disabled"),
            $("#login-loading").hide()),
            1 == e.status && window.location.reload());
        },
      }),
        e.preventDefault());
    }),
    $("#register-form").submit(function (e) {
      var s = $("#username").val(),
        t = md5(s + s7euu24fblrg914z);
      ($("#register-submit").prop("disabled", !0),
        $("#register-loading").show());
      var o = $(this).serializeArray();
      o.push({ name: "token", value: t });
      var a = $(this).attr("action");
      ($.ajax({
        url: a,
        type: "POST",
        data: o,
        dataType: "json",
        success: function (e) {
          if (($(".error-block").hide(), 0 == e.status)) {
            for (var s in e.messages)
              ($("#error-" + s).show(), $("#error-" + s).text(e.messages[s]));
            ($("#register-submit").removeAttr("disabled"),
              $("#register-loading").hide());
          }
          1 == e.status && window.location.reload();
        },
      }),
        e.preventDefault());
    }),
    $("#forgot-form").submit(function (e) {
      ($("#forgot-submit").prop("disabled", !0), $("#forgot-loading").show());
      var s = $(this).serializeArray();
      ($.ajax({
        url: base_url + "user/forgotPassword",
        type: "POST",
        data: s,
        dataType: "json",
        success: function (e) {
          (0 == e.status &&
            ($("#forgot-error-message").show(),
            $("#forgot-error-message").text(e.message)),
            1 == e.status &&
              ($("#forgot-success-message").show(),
              $("#forgot-success-message").text(e.message)),
            $("#forgot-submit").removeAttr("disabled"),
            $("#forgot-loading").hide());
        },
      }),
        e.preventDefault());
    }),
    $("#request-form").submit(function (e) {
      var s = $("#movie_name").val(),
        t = md5(s + s7euu24fblrg914z);
      ($("#request-submit").prop("disabled", !0), $("#request-loading").show());
      var o = $(this).serializeArray();
      o.push({ name: "token", value: t });
      var a = $(this).attr("action");
      ($.ajax({
        url: a,
        type: "POST",
        data: o,
        dataType: "json",
        success: function (e) {
          if (($(".error-block").hide(), 0 == e.status))
            for (var s in e.messages)
              ($("#error-" + s).show(), $("#error-" + s).text(e.messages[s]));
          (1 == e.status &&
            ($("#message-success").show(),
            setTimeout(function () {
              $("#message-success").hide();
            }, 5e3),
            document.getElementById("request-form").reset()),
            $("#request-submit").removeAttr("disabled"),
            $("#request-loading").hide());
        },
      }),
        e.preventDefault());
    }));
}),
  $("#donate-gift-card-form").submit(function (e) {
    var s = $(this).serializeArray(),
      t = $(this).attr("action");
    ($.ajax({
      url: t,
      type: "POST",
      data: s,
      dataType: "json",
      success: function (e) {
        if (($(".error-block").hide(), 0 == e.status))
          for (var s in e.messages)
            ($("#error-" + s).show(), $("#error-" + s).text(e.messages[s]));
        1 == e.status &&
          ($("#message-success").show(),
          setTimeout(function () {
            $("#message-success").hide();
          }, 5e3),
          document.getElementById("donate-gift-card-form").reset());
      },
    }),
      e.preventDefault());
  }),
  $.cookie("subscribe") ||
    setTimeout(function () {
      ($("#pop-subc").modal("show"),
        $.cookie("subscribe", 1, { expires: 1, path: "/" }));
    }, 1e4),
  $.cookie("subscribed") || $("#subs-block-home").show());
