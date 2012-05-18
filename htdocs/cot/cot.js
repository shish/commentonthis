var cot_base = "http://www.commentonthis.net/";

function cot_hash_node(node) {
	return Sha1.hash(node.text());
}

function cot_init_style() {
	var ss = document.createElement("link");
	ss.type = "text/css";
	ss.rel = "stylesheet";
	ss.href = cot_base+"cot/cot.css";
	document.getElementsByTagName("head")[0].appendChild(ss);
}

function cot_init(account_id, filter, canonical_base) {
	var canonical_base = canonical_base || window.location.href;
	var filter = filter || ".cot_item";

	cot_init_style();

	$(filter).each(function(idx, item_el_raw) {
		var item_el = $(item_el_raw);
		item_el.addClass("cot_item");
		if(!item_el.attr("id")) {
			item_el.attr("id", cot_hash_node(item_el));
		}
		item_el.data("snippet", item_el.text().substring(0, 150));

		var cbox_link_add = document.createElement("a");
		cbox_link_add.innerHTML = "Comment on this";
		$(cbox_link_add).attr("href", "#");
		$(cbox_link_add).click(function(e) {
			win = window.open(
				cot_base+"comments/new"+
				"?quote="+encodeURIComponent(item_el.data("snippet"))+
				"&page_owner="+encodeURIComponent(account_id)+
				"&page_url="+encodeURIComponent(canonical_base)+
				"&item_id="+encodeURIComponent(item_el.attr("id")),
				'New Comment',
				'height=200,width=450'
			);
			if(window.focus) {
				win.focus();
			}
			return false;
		});

		var cbox_link_view = document.createElement("a");
		cbox_link_view.innerHTML = "View current comments";
		$(cbox_link_view).attr("class", "cot_link_view");
		$(cbox_link_view).attr("href", cot_base+"comments?page="+encodeURIComponent(canonical_base)+"&item="+encodeURIComponent(item_el.attr("id")));
		$(cbox_link_view).data("item-id", item_el.attr("id"));

		var cbox_toggle_icon = document.createElement("img");
		cbox_toggle_icon.src = cot_base+"cot/cot.png";
		$(cbox_toggle_icon).attr("class", "cot_toggle_icon");

		var cbox = document.createElement("div");
		$(cbox).attr("class", "cot_linkbox");
		cbox.appendChild(cbox_link_add);
		cbox.appendChild(document.createElement("br"));
		cbox.appendChild(cbox_link_view);

		var cbox_toggle = document.createElement("div");
		$(cbox_toggle).attr("class", "cot_toggle");
		cbox_toggle.appendChild(cbox_toggle_icon);
		cbox_toggle.appendChild(cbox);

		item_el_raw.insertBefore(cbox_toggle, item_el_raw.firstChild);
	});
	$(".cot_link_add").each(function(idx, el) {
		var el = $(el);
	});
}
